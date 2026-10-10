using System;
using System.Collections.Generic;
using System.Linq;
using RimBridgeServer.Contracts;
using RimBridgeServer.Core;
using Verse;

namespace RimBridgeServer;

internal sealed class DiagnosticsCapabilityModule
{
	private readonly CapabilityRegistry _registry;

	private readonly OperationJournal _journal;

	private readonly LogJournal _logJournal;

	private readonly ConditionWaiter _waiter = new ConditionWaiter();

	public DiagnosticsCapabilityModule(OperationJournal journal, LogJournal logJournal, CapabilityRegistry registry)
	{
		_journal = journal ?? throw new ArgumentNullException("journal");
		_logJournal = logJournal ?? throw new ArgumentNullException("logJournal");
		_registry = registry ?? throw new ArgumentNullException("registry");
	}

	public object Ping()
	{
		return new
		{
			message = "pong",
			timestamp = DateTime.UtcNow
		};
	}

	public object GetGameInfo()
	{
		Game game = Current.Game;
		if (game == null)
		{
			return new
			{
				status = "no_game",
				message = "No game is currently loaded"
			};
		}
		return new
		{
			status = "game_loaded",
			ticksGame = game.tickManager.TicksGame,
			mapCount = (game.Maps?.Count ?? 0),
			selectedPawns = Find.Selector.SelectedPawns.Select(delegate(Pawn pawn)
			{
				Name name = pawn.Name;
				return ((name != null) ? name.ToStringShort : null) ?? ((Entity)pawn).LabelShort;
			}).ToList()
		};
	}

	public object GetOperation(string operationId)
	{
		OperationEnvelope operation = _journal.GetOperation(operationId);
		if (operation == null)
		{
			return new
			{
				success = false,
				message = "Operation '" + operationId + "' was not found in the journal."
			};
		}
		return new
		{
			success = true,
			trackedOperation = operation
		};
	}

	public object GetBridgeStatus()
	{
		return RimWorldWaits.GetBridgeStatus(_journal, _logJournal);
	}

	public object ListCapabilities(int limit = 200, string providerId = null, string category = null, string source = null, string query = null, bool includeParameters = true)
	{
		if (limit <= 0)
		{
			return new
			{
				success = true,
				totalCount = 0,
				returnedCount = 0,
				capabilities = Array.Empty<object>()
			};
		}
		List<CapabilityDescriptor> list = (from descriptor in _registry.GetCapabilities()
			where string.IsNullOrWhiteSpace(providerId) || string.Equals(descriptor.ProviderId, providerId, StringComparison.Ordinal)
			where string.IsNullOrWhiteSpace(category) || string.Equals(descriptor.Category, category, StringComparison.OrdinalIgnoreCase)
			where string.IsNullOrWhiteSpace(source) || string.Equals(descriptor.Source.ToString(), source, StringComparison.OrdinalIgnoreCase)
			where string.IsNullOrWhiteSpace(query) || MatchesCapabilityQuery(descriptor, query)
			select descriptor).ToList();
		List<object> list2 = (from descriptor in list.Take(limit)
			select DescribeCapability(descriptor, includeParameters)).ToList();
		return new
		{
			success = true,
			totalCount = list.Count,
			returnedCount = list2.Count,
			truncated = (list2.Count < list.Count),
			capabilities = list2
		};
	}

	public object GetCapability(string capabilityIdOrAlias)
	{
		try
		{
			CapabilityDescriptor descriptor = _registry.ResolveDescriptor(capabilityIdOrAlias);
			return new
			{
				success = true,
				requestedId = capabilityIdOrAlias,
				capability = DescribeCapability(descriptor, includeParameters: true)
			};
		}
		catch (Exception ex)
		{
			return new
			{
				success = false,
				message = ex.Message,
				requestedId = capabilityIdOrAlias
			};
		}
	}

	public object ListOperations(int limit = 20, bool includeResults = false)
	{
		return new
		{
			operations = _journal.GetRecentOperations(limit, includeResults)
		};
	}

	public object ListOperationEvents(int limit = 50, string eventType = null, long afterSequence = 0L, string operationId = null, bool includeDiagnostics = false)
	{
		IReadOnlyList<OperationEventRecord> source = _journal.GetRecentEvents(Math.Max(limit * 4, limit), eventType, afterSequence, operationId);
		if (!includeDiagnostics)
		{
			source = source.Where((OperationEventRecord entry) => !entry.CapabilityId.StartsWith("rimbridge.core/diagnostics/", StringComparison.Ordinal)).ToList();
		}
		return new
		{
			events = source.Take(limit).ToList()
		};
	}

	public object ListLogs(int limit = 50, string minimumLevel = "info", long afterSequence = 0L, string operationId = null, string rootOperationId = null, string capabilityId = null)
	{
		return new
		{
			logs = _logJournal.GetEntries(limit, minimumLevel, afterSequence, operationId, rootOperationId, capabilityId)
		};
	}

	public object WaitForOperation(string operationId, int timeoutMs = 10000, int pollIntervalMs = 50)
	{
		WaitOutcome waitOutcome = _waiter.WaitUntil(delegate
		{
			OperationEnvelope operation = _journal.GetOperation(operationId);
			if (operation == null)
			{
				return new WaitProbeResult
				{
					IsSatisfied = false,
					Message = "Waiting for operation '" + operationId + "' to appear in the journal."
				};
			}
			OperationStatus status = operation.Status;
			bool flag = (uint)(status - 2) <= 3u;
			bool flag2 = flag;
			return new WaitProbeResult
			{
				IsSatisfied = flag2,
				Message = (flag2 ? $"Operation '{operationId}' reached status {operation.Status}." : ("Waiting for operation '" + operationId + "' to reach a terminal status.")),
				Snapshot = operation
			};
		}, new WaitOptions
		{
			TimeoutMs = timeoutMs,
			PollIntervalMs = pollIntervalMs,
			TimeoutMessage = "Timed out waiting for operation '" + operationId + "'."
		});
		return new
		{
			success = waitOutcome.Satisfied,
			satisfied = waitOutcome.Satisfied,
			message = waitOutcome.Message,
			elapsedMs = waitOutcome.ElapsedMs,
			attempts = waitOutcome.Attempts,
			probeFailureCount = waitOutcome.ProbeFailureCount,
			lastProbeError = (string.IsNullOrWhiteSpace(waitOutcome.LastProbeError) ? null : waitOutcome.LastProbeError),
			trackedOperation = waitOutcome.Snapshot
		};
	}

	public object WaitForGameLoaded(int timeoutMs = 30000, int pollIntervalMs = 50, string readiness = "mapData", bool pauseIfNeeded = false, string targetReadiness = null, bool waitForVisualReady = false)
	{
		readiness = RimWorldWaits.ResolveReadinessInput(readiness, targetReadiness, waitForVisualReady);
		return RimWorldWaits.WaitForGameLoaded(timeoutMs, pollIntervalMs, readiness, pauseIfNeeded);
	}

	public object WaitForLongEventIdle(int timeoutMs = 30000, int pollIntervalMs = 100)
	{
		return RimWorldWaits.WaitForLongEventIdle(timeoutMs, pollIntervalMs);
	}

	private static bool MatchesCapabilityQuery(CapabilityDescriptor descriptor, string query)
	{
		string needle = query.Trim();
		if (needle.Length == 0)
		{
			return true;
		}
		if (!Contains(descriptor.Id, needle) && !Contains(descriptor.ProviderId, needle) && !Contains(descriptor.Category, needle) && !Contains(descriptor.Title, needle) && !Contains(descriptor.Summary, needle) && !GenCollection.Any<string>(descriptor.Aliases, (Predicate<string>)((string alias) => Contains(alias, needle))))
		{
			return GenCollection.Any<CapabilityParameterDescriptor>(descriptor.Parameters, (Predicate<CapabilityParameterDescriptor>)((CapabilityParameterDescriptor parameter) => Contains(parameter.Name, needle) || Contains(parameter.Description, needle)));
		}
		return true;
	}

	private static bool Contains(string value, string needle)
	{
		if (!string.IsNullOrWhiteSpace(value))
		{
			return value.IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0;
		}
		return false;
	}

	private static object DescribeCapability(CapabilityDescriptor descriptor, bool includeParameters)
	{
		return new
		{
			id = descriptor.Id,
			providerId = descriptor.ProviderId,
			category = descriptor.Category,
			title = descriptor.Title,
			summary = descriptor.Summary,
			source = descriptor.Source.ToString(),
			executionKind = descriptor.ExecutionKind.ToString(),
			supportedModes = ExpandSupportedModes(descriptor.SupportedModes),
			defaultRequestedMode = CapabilityExecutionMode.Wait.ToString(),
			emitsEvents = descriptor.EmitsEvents,
			resultType = descriptor.ResultType,
			aliases = descriptor.Aliases,
			parameters = (includeParameters ? descriptor.Parameters.Select((CapabilityParameterDescriptor parameter) => new
			{
				name = parameter.Name,
				parameterType = parameter.ParameterType,
				description = parameter.Description,
				required = parameter.Required,
				defaultValue = parameter.DefaultValue
			}).ToList() : null)
		};
	}

	private static string[] ExpandSupportedModes(CapabilityExecutionMode supportedModes)
	{
		return (from CapabilityExecutionMode mode in Enum.GetValues(typeof(CapabilityExecutionMode))
			where mode != CapabilityExecutionMode.None && (supportedModes & mode) == mode
			select mode.ToString()).ToArray();
	}
}
