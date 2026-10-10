using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using RimBridgeServer.Core;
using Verse;

namespace RimBridgeServer;

internal static class RimWorldModConfiguration
{
	private sealed class ModConfigurationEntrySnapshot
	{
		public string ModId { get; set; }

		public string PackageId { get; set; }

		public string PackageIdPlayerFacing { get; set; }

		public string PackageIdNonUnique { get; set; }

		public string Name { get; set; }

		public string ShortName { get; set; }

		public string FolderName { get; set; }

		public string RootDir { get; set; }

		public string Source { get; set; }

		public string Authors { get; set; }

		public string Version { get; set; }

		public bool Official { get; set; }

		public bool OnSteamWorkshop { get; set; }

		public bool IsCoreMod { get; set; }

		public bool Enabled { get; set; }

		public bool LoadedInSession { get; set; }

		public int? ActiveLoadOrder { get; set; }

		public int? LoadedSessionOrder { get; set; }

		public bool VersionCompatible { get; set; }

		public bool MadeForNewerVersion { get; set; }

		public bool HasConfigurationWarning { get; set; }

		public string ConfigurationWarning { get; set; }

		public bool HasVersionWarning { get; set; }

		public bool HasOrderingIssues { get; set; }

		public bool MatchesLoadedSession { get; set; }

		public List<string> UnsatisfiedDependencies { get; set; }

		public List<string> LoadBefore { get; set; }

		public List<string> LoadAfter { get; set; }

		public List<string> ForceLoadBefore { get; set; }

		public List<string> ForceLoadAfter { get; set; }

		public List<string> IncompatibleWith { get; set; }
	}

	private sealed class ModConfigurationSnapshot
	{
		public string ConfigPath { get; set; }

		public string CurrentConfigurationHash { get; set; }

		public string LoadedSessionHash { get; set; }

		public bool RestartRequired { get; set; }

		public List<string> RestartReasons { get; set; }

		public List<ModConfigurationEntrySnapshot> Mods { get; set; }

		public List<ModConfigurationEntrySnapshot> ActiveMods { get; set; }

		public List<ModConfigurationEntrySnapshot> LoadedSessionMods { get; set; }

		public int ConfigurationIssueCount { get; set; }

		public int VersionWarningCount { get; set; }

		public int OrderingIssueCount { get; set; }

		public int UnsatisfiedDependencyCount { get; set; }

		public int SessionMismatchCount { get; set; }
	}

	public static object ListModsResponse(bool includeInactive = true)
	{
		ModConfigurationSnapshot modConfigurationSnapshot = DescribeConfiguration();
		List<ModConfigurationEntrySnapshot> list = (includeInactive ? modConfigurationSnapshot.Mods : modConfigurationSnapshot.ActiveMods);
		return new
		{
			success = true,
			includeInactive = includeInactive,
			modCount = list.Count,
			activeCount = modConfigurationSnapshot.ActiveMods.Count,
			loadedSessionModCount = modConfigurationSnapshot.LoadedSessionMods.Count,
			restartRequired = modConfigurationSnapshot.RestartRequired,
			restartReasonCount = modConfigurationSnapshot.RestartReasons.Count,
			restartReasons = modConfigurationSnapshot.RestartReasons,
			sessionMismatchCount = modConfigurationSnapshot.SessionMismatchCount,
			mods = list.Select(ToResponseEntry).ToList()
		};
	}

	public static object GetModConfigurationStatusResponse()
	{
		return ToResponseStatus(DescribeConfiguration());
	}

	public static object SetModEnabledResponse(string modId, bool enabled, bool save = true, bool allowDisableCore = false)
	{
		if (!TryResolveMod(modId, out var mod, out var normalizedQuery, out var error))
		{
			return Failure(error, normalizedQuery, null, null, includeStatus: true);
		}
		ModConfigurationSnapshot modConfigurationSnapshot = DescribeConfiguration();
		ModConfigurationEntrySnapshot modConfigurationEntrySnapshot = GenCollection.FirstOrDefault<ModConfigurationEntrySnapshot>(modConfigurationSnapshot.Mods, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot candidate) => string.Equals(candidate.ModId, GetModId(mod), StringComparison.Ordinal)));
		bool flag = modConfigurationEntrySnapshot?.Enabled ?? ModsConfig.IsActive(mod);
		if (!enabled && mod.IsCoreMod && !allowDisableCore)
		{
			return Failure("Refusing to disable core mod '" + mod.Name + "'. Pass allowDisableCore=true to override this guard.", normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
		}
		if (enabled && TryFindConflictingActiveMod(mod, out var conflictingMod))
		{
			return Failure("Cannot enable '" + mod.Name + "' while '" + conflictingMod.Name + "' with the same package id is already active.", normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
		}
		bool flag2 = flag != enabled;
		if (flag2)
		{
			try
			{
				ModsConfig.SetActive(mod, enabled);
				if (save)
				{
					ModsConfig.Save();
				}
			}
			catch (Exception ex)
			{
				return Failure("Updating enabled state for '" + normalizedQuery + "' failed: " + ex.Message, normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
			}
		}
		ModConfigurationSnapshot modConfigurationSnapshot2 = DescribeConfiguration();
		ModConfigurationEntrySnapshot modConfigurationEntrySnapshot2 = GenCollection.FirstOrDefault<ModConfigurationEntrySnapshot>(modConfigurationSnapshot2.Mods, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot candidate) => string.Equals(candidate.ModId, GetModId(mod), StringComparison.Ordinal)));
		bool currentEnabled = modConfigurationEntrySnapshot2?.Enabled ?? enabled;
		return new
		{
			success = true,
			requestedModId = normalizedQuery,
			changed = flag2,
			saved = (flag2 && save),
			previousEnabled = flag,
			currentEnabled = currentEnabled,
			message = (flag2 ? ((enabled ? "Enabled" : "Disabled") + " mod '" + (modConfigurationEntrySnapshot2?.Name ?? mod.Name) + "'.") : ("Mod '" + (modConfigurationEntrySnapshot2?.Name ?? mod.Name) + "' was already " + (enabled ? "enabled" : "disabled") + ".")),
			mod = ((modConfigurationEntrySnapshot2 == null) ? null : ToResponseEntry(modConfigurationEntrySnapshot2)),
			configurationStatus = ToResponseStatus(modConfigurationSnapshot2)
		};
	}

	public static object ReorderModResponse(string modId, int targetIndex, bool save = true)
	{
		if (!TryResolveMod(modId, out var mod, out var normalizedQuery, out var error))
		{
			return Failure(error, normalizedQuery, null, null, includeStatus: true);
		}
		ModConfigurationSnapshot modConfigurationSnapshot = DescribeConfiguration();
		ModConfigurationEntrySnapshot modConfigurationEntrySnapshot = GenCollection.FirstOrDefault<ModConfigurationEntrySnapshot>(modConfigurationSnapshot.Mods, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot candidate) => string.Equals(candidate.ModId, GetModId(mod), StringComparison.Ordinal)));
		if (modConfigurationEntrySnapshot == null || !modConfigurationEntrySnapshot.Enabled || !modConfigurationEntrySnapshot.ActiveLoadOrder.HasValue)
		{
			return Failure("Mod '" + normalizedQuery + "' is not currently enabled, so it has no active load-order position to reorder.", normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
		}
		if (targetIndex < 0 || targetIndex >= modConfigurationSnapshot.ActiveMods.Count)
		{
			return Failure($"Target index {targetIndex} is out of range for the current active mod list (0-{Math.Max(0, modConfigurationSnapshot.ActiveMods.Count - 1)}).", normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
		}
		bool flag;
		string text = default(string);
		try
		{
			flag = ModsConfig.TryReorder(modConfigurationEntrySnapshot.ActiveLoadOrder.Value, targetIndex, ref text);
			if (flag && save)
			{
				ModsConfig.Save();
			}
		}
		catch (Exception ex)
		{
			return Failure("Reordering mod '" + normalizedQuery + "' failed: " + ex.Message, normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
		}
		if (!flag && !string.IsNullOrWhiteSpace(text))
		{
			return Failure(text, normalizedQuery, modConfigurationEntrySnapshot, modConfigurationSnapshot);
		}
		ModConfigurationSnapshot modConfigurationSnapshot2 = DescribeConfiguration();
		ModConfigurationEntrySnapshot modConfigurationEntrySnapshot2 = GenCollection.FirstOrDefault<ModConfigurationEntrySnapshot>(modConfigurationSnapshot2.Mods, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot candidate) => string.Equals(candidate.ModId, GetModId(mod), StringComparison.Ordinal)));
		return new
		{
			success = true,
			requestedModId = normalizedQuery,
			changed = flag,
			saved = (flag && save),
			previousIndex = modConfigurationEntrySnapshot.ActiveLoadOrder,
			targetIndex = targetIndex,
			currentIndex = modConfigurationEntrySnapshot2?.ActiveLoadOrder,
			message = (flag ? $"Moved mod '{modConfigurationEntrySnapshot2?.Name ?? mod.Name}' to active load-order index {modConfigurationEntrySnapshot2?.ActiveLoadOrder ?? targetIndex}." : $"Mod '{modConfigurationEntrySnapshot2?.Name ?? mod.Name}' was already at active load-order index {targetIndex}."),
			mod = ((modConfigurationEntrySnapshot2 == null) ? null : ToResponseEntry(modConfigurationEntrySnapshot2)),
			configurationStatus = ToResponseStatus(modConfigurationSnapshot2)
		};
	}

	private static ModConfigurationSnapshot DescribeConfiguration()
	{
		IReadOnlyList<ModMetaData> installedMods = GetInstalledMods();
		List<ModMetaData> source = (from mod in ModsConfig.ActiveModsInLoadOrder?.OfType<ModMetaData>()
			where mod != null
			select mod).ToList() ?? new List<ModMetaData>();
		List<ModContentPack> source2 = (from mod in LoadedModManager.RunningModsListForReading?.OfType<ModContentPack>()
			where mod != null
			select mod).ToList() ?? new List<ModContentPack>();
		Dictionary<string, string> warningsByPackageId = ModsConfig.GetModWarnings() ?? new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
		Dictionary<string, int> activeOrderByModId = source.Select((ModMetaData mod, int index) => new
		{
			ModId = GetModId(mod),
			Index = index
		}).ToDictionary(item => item.ModId, item => item.Index, StringComparer.Ordinal);
		Dictionary<string, int> loadedOrderByModId = source2.Select((ModContentPack mod, int index) => new
		{
			ModId = GetModId(mod),
			Index = index
		}).ToDictionary(item => item.ModId, item => item.Index, StringComparer.Ordinal);
		List<ModConfigurationEntrySnapshot> list = (from mod in installedMods
			select DescribeMod(mod, warningsByPackageId, activeOrderByModId, loadedOrderByModId) into mod
			orderby (!mod.Enabled) ? 1 : 0, mod.ActiveLoadOrder ?? int.MaxValue
			select mod).ThenBy((ModConfigurationEntrySnapshot mod) => mod.Name, StringComparer.OrdinalIgnoreCase).ThenBy((ModConfigurationEntrySnapshot mod) => mod.PackageId, StringComparer.OrdinalIgnoreCase).ToList();
		List<ModConfigurationEntrySnapshot> list2 = (from mod in list
			where mod.Enabled
			orderby mod.ActiveLoadOrder ?? int.MaxValue
			select mod).ToList();
		List<ModConfigurationEntrySnapshot> list3 = (from mod in list
			where mod.LoadedInSession
			orderby mod.LoadedSessionOrder ?? int.MaxValue
			select mod).ToList();
		List<string> list4 = list2.Select((ModConfigurationEntrySnapshot mod) => mod.ModId).ToList();
		List<string> list5 = list3.Select((ModConfigurationEntrySnapshot mod) => mod.ModId).ToList();
		List<string> list6 = DescribeRestartReasons(list4, list5);
		return new ModConfigurationSnapshot
		{
			ConfigPath = GenFilePaths.ModsConfigFilePath,
			CurrentConfigurationHash = ComputeFingerprint(list4),
			LoadedSessionHash = ComputeFingerprint(list5),
			RestartRequired = (list6.Count > 0),
			RestartReasons = list6,
			Mods = list,
			ActiveMods = list2,
			LoadedSessionMods = list3,
			ConfigurationIssueCount = GenCollection.Count<ModConfigurationEntrySnapshot>(list2, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot mod) => mod.HasConfigurationWarning)),
			VersionWarningCount = GenCollection.Count<ModConfigurationEntrySnapshot>(list2, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot mod) => mod.HasVersionWarning)),
			OrderingIssueCount = GenCollection.Count<ModConfigurationEntrySnapshot>(list2, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot mod) => mod.HasOrderingIssues)),
			UnsatisfiedDependencyCount = GenCollection.Count<ModConfigurationEntrySnapshot>(list2, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot mod) => mod.UnsatisfiedDependencies.Count > 0)),
			SessionMismatchCount = GenCollection.Count<ModConfigurationEntrySnapshot>(list, (Predicate<ModConfigurationEntrySnapshot>)((ModConfigurationEntrySnapshot mod) => !mod.MatchesLoadedSession))
		};
	}

	private static ModConfigurationEntrySnapshot DescribeMod(ModMetaData mod, IReadOnlyDictionary<string, string> warningsByPackageId, IReadOnlyDictionary<string, int> activeOrderByModId, IReadOnlyDictionary<string, int> loadedOrderByModId)
	{
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		string modId = GetModId(mod);
		string value;
		string text = NormalizeString(warningsByPackageId.TryGetValue(mod.PackageId ?? string.Empty, out value) ? value : string.Empty);
		activeOrderByModId.TryGetValue(modId, out var value2);
		loadedOrderByModId.TryGetValue(modId, out var value3);
		bool flag = activeOrderByModId.ContainsKey(modId);
		bool flag2 = loadedOrderByModId.ContainsKey(modId);
		bool flag3 = flag || ModsConfig.IsActive(mod);
		bool matchesLoadedSession = flag3 == flag2 && (!flag3 || value2 == value3);
		return new ModConfigurationEntrySnapshot
		{
			ModId = modId,
			PackageId = NormalizeString(mod.PackageId),
			PackageIdPlayerFacing = NormalizeString(mod.PackageIdPlayerFacing),
			PackageIdNonUnique = NormalizeString(mod.PackageIdNonUnique),
			Name = NormalizeString(mod.Name),
			ShortName = NormalizeString(mod.ShortName),
			FolderName = NormalizeString(mod.FolderName),
			RootDir = NormalizeRootDir(mod),
			Source = ((object)mod.Source/*cast due to .constrained prefix*/).ToString(),
			Authors = NormalizeString(mod.AuthorsString),
			Version = NormalizeString(mod.ModVersion),
			Official = mod.Official,
			OnSteamWorkshop = mod.OnSteamWorkshop,
			IsCoreMod = mod.IsCoreMod,
			Enabled = flag3,
			LoadedInSession = flag2,
			ActiveLoadOrder = (flag ? new int?(value2) : ((int?)null)),
			LoadedSessionOrder = (flag2 ? new int?(value3) : ((int?)null)),
			VersionCompatible = mod.VersionCompatible,
			MadeForNewerVersion = mod.MadeForNewerVersion,
			HasConfigurationWarning = !string.IsNullOrWhiteSpace(text),
			ConfigurationWarning = text,
			HasVersionWarning = !mod.VersionCompatible,
			HasOrderingIssues = (flag && ModsConfig.ModHasAnyOrderingIssues(mod)),
			MatchesLoadedSession = matchesLoadedSession,
			UnsatisfiedDependencies = NormalizeList(mod.UnsatisfiedDependencies()),
			LoadBefore = NormalizeList(mod.LoadBefore),
			LoadAfter = NormalizeList(mod.LoadAfter),
			ForceLoadBefore = NormalizeList(mod.ForceLoadBefore),
			ForceLoadAfter = NormalizeList(mod.ForceLoadAfter),
			IncompatibleWith = NormalizeList(mod.IncompatibleWith)
		};
	}

	private static IReadOnlyList<ModMetaData> GetInstalledMods()
	{
		ModLister.EnsureInit();
		return (from mod in ModLister.AllInstalledMods?.OfType<ModMetaData>()
			where mod != null
			select mod).OrderBy((ModMetaData mod) => mod.Name, StringComparer.OrdinalIgnoreCase).ThenBy((ModMetaData mod) => mod.PackageId, StringComparer.OrdinalIgnoreCase).ToList() ?? new List<ModMetaData>();
	}

	private static bool TryResolveMod(string modId, out ModMetaData mod, out string normalizedQuery, out string error)
	{
		mod = null;
		normalizedQuery = modId?.Trim() ?? string.Empty;
		error = string.Empty;
		if (string.IsNullOrWhiteSpace(normalizedQuery))
		{
			error = "A mod id, package id, package id (player-facing), name, folder name, or root path is required.";
			return false;
		}
		IReadOnlyList<ModMetaData> installedMods = GetInstalledMods();
		string query = normalizedQuery;
		mod = installedMods.FirstOrDefault((ModMetaData candidate) => string.Equals(GetModId(candidate), query, StringComparison.Ordinal));
		if (mod != null)
		{
			return true;
		}
		List<ModMetaData> list = installedMods.Where((ModMetaData candidate) => MatchesCandidate(candidate, query)).ToList();
		if (list.Count == 1)
		{
			mod = list[0];
			return true;
		}
		if (list.Count > 1)
		{
			error = "Query '" + normalizedQuery + "' matched multiple installed mods: " + string.Join(", ", list.Select(GetModId)) + ". Use the exact modId from rimworld/list_mods.";
			return false;
		}
		error = "Could not find an installed mod matching '" + normalizedQuery + "'.";
		return false;
	}

	private static bool MatchesCandidate(ModMetaData mod, string query)
	{
		if (!string.Equals(mod.PackageId, query, StringComparison.OrdinalIgnoreCase) && !string.Equals(mod.PackageIdPlayerFacing, query, StringComparison.OrdinalIgnoreCase) && !string.Equals(mod.PackageIdNonUnique, query, StringComparison.OrdinalIgnoreCase) && !string.Equals(mod.Name, query, StringComparison.OrdinalIgnoreCase) && !string.Equals(mod.ShortName, query, StringComparison.OrdinalIgnoreCase) && !string.Equals(mod.FolderName, query, StringComparison.OrdinalIgnoreCase))
		{
			return string.Equals(NormalizeRootDir(mod), query, StringComparison.OrdinalIgnoreCase);
		}
		return true;
	}

	private static bool TryFindConflictingActiveMod(ModMetaData mod, out ModMetaData conflictingMod)
	{
		conflictingMod = GetInstalledMods().FirstOrDefault((ModMetaData candidate) => !string.Equals(GetModId(candidate), GetModId(mod), StringComparison.Ordinal) && candidate.Active && candidate.SamePackageId(mod.PackageId, true));
		return conflictingMod != null;
	}

	private static string GetModId(ModMetaData mod)
	{
		return ModConfigurationIds.CreateId(mod.PackageId ?? mod.Name ?? mod.FolderName ?? "unknown-mod", NormalizeRootDir(mod));
	}

	private static string GetModId(ModContentPack mod)
	{
		return ModConfigurationIds.CreateId(mod.PackageId ?? mod.Name ?? mod.FolderName ?? "unknown-mod", NormalizeString(mod.RootDir));
	}

	private static string NormalizeRootDir(ModMetaData mod)
	{
		return mod.RootDir?.FullName?.Trim() ?? string.Empty;
	}

	private static string NormalizeString(string value)
	{
		if (!string.IsNullOrWhiteSpace(value))
		{
			return value.Trim();
		}
		return string.Empty;
	}

	private static List<string> NormalizeList(IEnumerable<string> values)
	{
		return (from value in values?.Where((string value) => !string.IsNullOrWhiteSpace(value))
			select value.Trim()).ToList() ?? new List<string>();
	}

	private static List<string> DescribeRestartReasons(IReadOnlyList<string> currentConfigurationIds, IReadOnlyList<string> loadedSessionIds)
	{
		List<string> list = new List<string>();
		if (currentConfigurationIds.SequenceEqual(loadedSessionIds, StringComparer.Ordinal))
		{
			return list;
		}
		HashSet<string> hashSet = new HashSet<string>(currentConfigurationIds, StringComparer.Ordinal);
		HashSet<string> hashSet2 = new HashSet<string>(loadedSessionIds, StringComparer.Ordinal);
		if (!hashSet.SetEquals(hashSet2))
		{
			list.Add("active_mod_set_differs_from_loaded_session");
			return list;
		}
		list.Add("active_mod_order_differs_from_loaded_session");
		return list;
	}

	private static string ComputeFingerprint(IEnumerable<string> values)
	{
		string s = string.Join("\n", values ?? Array.Empty<string>());
		byte[] bytes = Encoding.UTF8.GetBytes(s);
		using SHA256 sHA = SHA256.Create();
		return string.Concat(from value in sHA.ComputeHash(bytes).Take(8)
			select value.ToString("x2"));
	}

	private static object ToResponseStatus(ModConfigurationSnapshot snapshot)
	{
		return new
		{
			success = true,
			configPath = snapshot.ConfigPath,
			installedModCount = snapshot.Mods.Count,
			activeModCount = snapshot.ActiveMods.Count,
			loadedSessionModCount = snapshot.LoadedSessionMods.Count,
			configurationIssueCount = snapshot.ConfigurationIssueCount,
			versionWarningCount = snapshot.VersionWarningCount,
			orderingIssueCount = snapshot.OrderingIssueCount,
			unsatisfiedDependencyCount = snapshot.UnsatisfiedDependencyCount,
			sessionMismatchCount = snapshot.SessionMismatchCount,
			restartRequired = snapshot.RestartRequired,
			restartReasonCount = snapshot.RestartReasons.Count,
			restartReasons = snapshot.RestartReasons,
			currentConfigurationHash = snapshot.CurrentConfigurationHash,
			loadedSessionHash = snapshot.LoadedSessionHash,
			currentActiveModIds = snapshot.ActiveMods.Select((ModConfigurationEntrySnapshot mod) => mod.ModId).ToList(),
			loadedSessionModIds = snapshot.LoadedSessionMods.Select((ModConfigurationEntrySnapshot mod) => mod.ModId).ToList(),
			activeMods = snapshot.ActiveMods.Select(ToResponseEntry).ToList(),
			loadedSessionMods = snapshot.LoadedSessionMods.Select(ToResponseEntry).ToList()
		};
	}

	private static object ToResponseEntry(ModConfigurationEntrySnapshot snapshot)
	{
		return new
		{
			modId = snapshot.ModId,
			packageId = snapshot.PackageId,
			packageIdPlayerFacing = snapshot.PackageIdPlayerFacing,
			packageIdNonUnique = snapshot.PackageIdNonUnique,
			name = snapshot.Name,
			shortName = snapshot.ShortName,
			folderName = snapshot.FolderName,
			rootDir = snapshot.RootDir,
			source = snapshot.Source,
			authors = snapshot.Authors,
			version = snapshot.Version,
			official = snapshot.Official,
			onSteamWorkshop = snapshot.OnSteamWorkshop,
			isCoreMod = snapshot.IsCoreMod,
			enabled = snapshot.Enabled,
			loadedInSession = snapshot.LoadedInSession,
			activeLoadOrder = snapshot.ActiveLoadOrder,
			loadedSessionOrder = snapshot.LoadedSessionOrder,
			versionCompatible = snapshot.VersionCompatible,
			madeForNewerVersion = snapshot.MadeForNewerVersion,
			hasConfigurationWarning = snapshot.HasConfigurationWarning,
			configurationWarning = snapshot.ConfigurationWarning,
			hasVersionWarning = snapshot.HasVersionWarning,
			hasOrderingIssues = snapshot.HasOrderingIssues,
			matchesLoadedSession = snapshot.MatchesLoadedSession,
			unsatisfiedDependencies = snapshot.UnsatisfiedDependencies,
			loadBefore = snapshot.LoadBefore,
			loadAfter = snapshot.LoadAfter,
			forceLoadBefore = snapshot.ForceLoadBefore,
			forceLoadAfter = snapshot.ForceLoadAfter,
			incompatibleWith = snapshot.IncompatibleWith
		};
	}

	private static object Failure(string message, string requestedModId, ModConfigurationEntrySnapshot mod = null, ModConfigurationSnapshot snapshot = null, bool includeStatus = false)
	{
		ModConfigurationSnapshot modConfigurationSnapshot = snapshot ?? (includeStatus ? DescribeConfiguration() : null);
		return new
		{
			success = false,
			message = message,
			requestedModId = requestedModId,
			mod = ((mod == null) ? null : ToResponseEntry(mod)),
			configurationStatus = ((modConfigurationSnapshot == null) ? null : ToResponseStatus(modConfigurationSnapshot))
		};
	}
}
