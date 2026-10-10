using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace EdB.PrepareCarefully;

public class ControllerPage
{
	public ModState State { get; set; }

	public ViewState ViewState { get; set; }

	public ControllerTabViewPawns PawnTabViewController { get; set; }

	public ControllerTabViewRelationships RelationshipTabViewController { get; set; }

	public CostCalculator CostCalculator { get; set; }

	public PawnCustomizer PawnCustomizer { get; set; }

	public ManagerPawns ManagerPawns { get; set; }

	public ManagerEquipment ManagerEquipment { get; set; }

	public ManagerRelationships ManagerRelationships { get; set; }

	public PresetLoader PresetLoader { get; set; }

	public PresetSaver PresetSaver { get; set; }

	public void PostConstruct()
	{
		PawnTabViewController.Initialize();
	}

	public bool UseLargeUI()
	{
		string[] obj = new string[5] { "Prepare Carefully window size: [", null, null, null, null };
		float x = Page.StandardSize.x;
		obj[1] = x.ToString();
		obj[2] = " x ";
		x = Page.StandardSize.y;
		obj[3] = x.ToString();
		obj[4] = "]";
		Logger.Debug(string.Concat(obj));
		Logger.Debug("Screen: [" + Screen.width + ", " + Screen.height + "], dpi = " + Screen.dpi + ", resolution = " + Screen.currentResolution.ToString());
		Logger.Debug("Screen safe area: " + Screen.safeArea.ToString());
		Logger.Debug("UI scale: " + Prefs.UIScale);
		Vector2 vector = new Vector2(Screen.safeArea.width / Prefs.UIScale, Screen.safeArea.height / Prefs.UIScale);
		Vector2 vector2 = new Vector2(64f, 64f) / Prefs.UIScale;
		vector -= vector2;
		Vector2 vector3 = new Vector2(1350f, Page.StandardSize.y);
		if (vector.x >= vector3.x && vector.y >= vector3.y)
		{
			return true;
		}
		return false;
	}

	public bool CancellingRequiresConfirmation()
	{
		return true;
	}

	public void CancelCustomizations()
	{
		foreach (Pawn startingAndOptionalPawn in Find.GameInitData.startingAndOptionalPawns)
		{
			if (State.OriginalPawnCustomizations.TryGetValue(startingAndOptionalPawn, out var value))
			{
				PawnCustomizer.ApplyAllCustomizationsToPawn(startingAndOptionalPawn, value);
			}
			else
			{
				Logger.Warning($"There may have been a problem undoing all pawn customizations.  The original state of a pawn was not stored properly");
			}
		}
		foreach (CustomizedPawn allPawn in State.Customizations.AllPawns)
		{
			if (allPawn.Pawn != null && !Find.GameInitData.startingAndOptionalPawns.Contains(allPawn.Pawn))
			{
				ManagerPawns.DestroyPawn(allPawn.Pawn);
			}
		}
	}

	public bool Validate()
	{
		return true;
	}

	public void StartGame()
	{
		PreparePawns();
		PrepareRelationships();
		PrepareEquipment();
		Page_ConfigureStartingPawns originalPage = State.OriginalPage;
		if (originalPage != null)
		{
			Page next = originalPage.next;
			Action nextAct = originalPage.nextAct;
			if (next != null)
			{
				Find.WindowStack.Add(next);
			}
			nextAct?.Invoke();
			TutorSystem.Notify_Event("PageClosed");
			TutorSystem.Notify_Event("GoToNextPage");
			originalPage.Close();
		}
	}

	public void PreparePawns()
	{
		List<Pawn> list = new List<Pawn>();
		HashSet<Pawn> hashSet = new HashSet<Pawn>();
		foreach (CustomizedPawn allPawn in State.Customizations.AllPawns)
		{
			allPawn.Pawn.SetFactionDirect(Faction.OfPlayer);
			if (allPawn.Type == CustomizedPawnType.Colony)
			{
				if (allPawn.Pawn.workSettings == null)
				{
					allPawn.Pawn.workSettings = new Pawn_WorkSettings(allPawn.Pawn);
				}
				allPawn.Pawn.workSettings.EnableAndInitialize();
			}
			list.Add(allPawn.Pawn);
			hashSet.Add(allPawn.Pawn);
			IEnumerable<CustomizedPossession> source = allPawn.Customizations.Possessions.Where((CustomizedPossession p) => p.ThingDef != null && p.Count > 0);
			Find.GameInitData.startingPossessions[allPawn.Pawn] = source.Select((CustomizedPossession p) => new ThingDefCount(p.ThingDef, p.Count)).ToList();
		}
		List<Pawn> list2 = new List<Pawn>();
		foreach (Pawn key in Find.GameInitData.startingPossessions.Keys)
		{
			if (!hashSet.Contains(key))
			{
				list2.Add(key);
			}
		}
		foreach (Pawn item in list2)
		{
			Find.GameInitData.startingPossessions.Remove(item);
		}
		Logger.Debug("Destroy any pawn that is not in our carefully prepared pawn list:");
		foreach (Pawn startingAndOptionalPawn in Find.GameInitData.startingAndOptionalPawns)
		{
			if (!State.Customizations.AllPawns.Select((CustomizedPawn p) => p.Pawn).Contains(startingAndOptionalPawn))
			{
				Logger.Debug("    Destroyed starting pawn: " + startingAndOptionalPawn.LabelShort);
				ManagerPawns.DestroyPawn(startingAndOptionalPawn);
			}
			else
			{
				Logger.Debug("    Kept starting pawn: " + startingAndOptionalPawn.LabelShort);
			}
		}
		Find.GameInitData.startingPawnCount = State.Customizations.ColonyPawns.Count;
		Find.GameInitData.startingAndOptionalPawns = list;
	}

	public void PrepareRelationships()
	{
		RelationshipTabViewController.RelationshipManager.GetRelationshipBuilder().Build();
	}

	public void PrepareEquipment()
	{
		List<ScenPart> fieldValue = ReflectionUtil.GetFieldValue<List<ScenPart>>(Find.Scenario, "parts");
		List<ScenPart> list = new List<ScenPart>();
		foreach (ScenPart item in fieldValue)
		{
			if (!State.ReplacedScenarioParts.Contains(item))
			{
				list.Add(item);
			}
		}
		foreach (CustomizedEquipment item2 in State.Customizations.Equipment)
		{
			list.AddRange(from p in CreateScenarioPartForCustomizedEquipment(item2)
				where p != null
				select p);
		}
		ReflectionUtil.SetFieldValue(Find.Scenario, "parts", list);
	}

	public bool ShouldReplaceScenarioPart(ScenPart part)
	{
		if (part.GetType() == typeof(ScenPart_ScatterThingsNearPlayerStart))
		{
			return true;
		}
		if (part.GetType() == typeof(ScenPart_StartingThing_Defined))
		{
			return true;
		}
		return false;
	}

	public IEnumerable<ScenPart> CreateScenarioPartForCustomizedEquipment(CustomizedEquipment equipment)
	{
		Logger.Debug($"AddScenarioPartForCustomizedEquipment({equipment.EquipmentOption?.ThingDef?.defName}), Animal = {equipment.Animal}, Mech = {equipment.Mech}");
		if (equipment.Animal)
		{
			ScenPart scenPart = CreateStartingAnimalScenarioPart(equipment);
			if (scenPart != null)
			{
				return new List<ScenPart> { scenPart };
			}
			Logger.Warning("Failed to add animal scene part");
			return new List<ScenPart>();
		}
		if (equipment.Mech)
		{
			return CreateStartingMechScenarioParts(equipment);
		}
		EquipmentSpawnType? equipmentSpawnType = equipment.SpawnType;
		if (equipment.EquipmentOption.RestrictedSpawnType && equipment.EquipmentOption.DefaultSpawnType != equipmentSpawnType)
		{
			equipmentSpawnType = equipment.EquipmentOption.DefaultSpawnType;
		}
		if (equipmentSpawnType == EquipmentSpawnType.SpawnsWith)
		{
			return new List<ScenPart> { CreateStartsWithScenarioPart(equipment) };
		}
		if (equipmentSpawnType == EquipmentSpawnType.SpawnsNear)
		{
			return new List<ScenPart> { CreateScatterThingsNearScenarioPart(equipment) };
		}
		return Enumerable.Empty<ScenPart>();
	}

	public ScenPart CreateStartsWithScenarioPart(CustomizedEquipment equipment)
	{
		ScenPart_StartingThing_Defined obj = new ScenPart_StartingThing_Defined
		{
			def = DefDatabase<ScenPartDef>.GetNamedSilentFail("StartingThing_Defined")
		};
		obj.SetPrivateField("thingDef", equipment.EquipmentOption?.ThingDef);
		obj.SetPrivateField("stuff", equipment.StuffDef);
		obj.SetPrivateField("count", equipment.Count);
		obj.SetPrivateField("quality", equipment.Quality);
		return obj;
	}

	public ScenPart CreateScatterThingsNearScenarioPart(CustomizedEquipment equipment)
	{
		ScenPart_ScatterThingsNearPlayerStart obj = new ScenPart_ScatterThingsNearPlayerStart
		{
			def = DefDatabase<ScenPartDef>.GetNamedSilentFail("ScatterThingsNearPlayerStart")
		};
		obj.SetPrivateField("thingDef", equipment.EquipmentOption?.ThingDef);
		obj.SetPrivateField("stuff", equipment.StuffDef);
		obj.SetPrivateField("count", equipment.Count);
		obj.SetPrivateField("quality", equipment.Quality);
		return obj;
	}

	public ScenPart CreateStartingAnimalScenarioPart(CustomizedEquipment equipment)
	{
		if (equipment.EquipmentOption.RandomAnimal)
		{
			return CreateRandomStartingAnimalScenarioPart(equipment);
		}
		if (equipment.Gender.HasValue)
		{
			return CreateStartingAnimalWithSpecificGenderScenarioPart(equipment);
		}
		return CreateStartingAnimalWithRandomGenderScenarioPart(equipment);
	}

	public IEnumerable<ScenPart> CreateStartingMechScenarioParts(CustomizedEquipment equipment)
	{
		if (equipment.EquipmentOption.RandomMech)
		{
			return CreateRandomStartingMechScenarioParts(equipment);
		}
		return CreateDefinedStartingMechScenarioParts(equipment);
	}

	public IEnumerable<ScenPart> CreateDefinedStartingMechScenarioParts(CustomizedEquipment equipment)
	{
		ScenPartDef scenPartDef = DefDatabase<ScenPartDef>.GetNamedSilentFail("StartingMech");
		if (scenPartDef == null)
		{
			Logger.Warning("Could not find definition for starting mech scenario part.  Cannot add scenario part");
			yield break;
		}
		PawnKindDef pawnKindDef = FindPawnKindDefForRace(equipment);
		if (pawnKindDef == null)
		{
			Logger.Warning($"Could not spawn selected mech ({equipment.EquipmentOption?.ThingDef?.defName}). Could not find matching pawn kind");
			yield break;
		}
		for (int i = 0; i < equipment.Count; i++)
		{
			ScenPart_StartingMech scenPart_StartingMech = new ScenPart_StartingMech
			{
				def = scenPartDef
			};
			scenPart_StartingMech.SetPrivateField("mechKind", pawnKindDef);
			scenPart_StartingMech.SetPrivateField("overseenByPlayerPawnChance", equipment.OverseenChance);
			yield return scenPart_StartingMech;
		}
	}

	public IEnumerable<ScenPart> CreateRandomStartingMechScenarioParts(CustomizedEquipment equipment)
	{
		ScenPartDef scenPartDef = DefDatabase<ScenPartDef>.GetNamedSilentFail("StartingMech");
		if (scenPartDef == null)
		{
			Logger.Warning("Could not find definition for starting mech scenario part.  Cannot add scenario part");
			yield break;
		}
		for (int i = 0; i < equipment.Count; i++)
		{
			ScenPart_StartingMech scenPart_StartingMech = new ScenPart_StartingMech
			{
				def = scenPartDef
			};
			scenPart_StartingMech.SetPrivateField("overseenByPlayerPawnChance", equipment.OverseenChance);
			yield return scenPart_StartingMech;
		}
	}

	public ScenPart CreateRandomStartingAnimalScenarioPart(CustomizedEquipment equipment)
	{
		ScenPartDef namedSilentFail = DefDatabase<ScenPartDef>.GetNamedSilentFail("StartingAnimal");
		if (namedSilentFail == null)
		{
			Logger.Warning("Could not find definition for starting animal scenario part.  Cannot add scenario part");
			return null;
		}
		ScenPart_StartingAnimal obj = new ScenPart_StartingAnimal
		{
			def = namedSilentFail
		};
		obj.SetPrivateField("count", equipment.Count);
		return obj;
	}

	public ScenPart CreateStartingAnimalWithRandomGenderScenarioPart(CustomizedEquipment equipment)
	{
		ScenPartDef namedSilentFail = DefDatabase<ScenPartDef>.GetNamedSilentFail("StartingAnimal");
		if (namedSilentFail == null)
		{
			Logger.Warning("Could not find definition for starting animal scenario part.  Cannot add scenario part");
			return null;
		}
		PawnKindDef pawnKindDef = FindPawnKindDefForRace(equipment);
		if (pawnKindDef == null)
		{
			Logger.Warning($"Could not spawn selected animal ({equipment.EquipmentOption?.ThingDef?.defName}). Could not find matching pawn kind");
			return null;
		}
		ScenPart_StartingAnimal obj = new ScenPart_StartingAnimal
		{
			def = namedSilentFail
		};
		obj.SetPrivateField("animalKind", pawnKindDef);
		obj.SetPrivateField("count", equipment.Count);
		return obj;
	}

	public ScenPart CreateStartingAnimalWithSpecificGenderScenarioPart(CustomizedEquipment equipment)
	{
		PawnKindDef pawnKindDef = FindPawnKindDefForRace(equipment);
		if (pawnKindDef == null)
		{
			Logger.Warning($"Could not spawn selected animal ({equipment.EquipmentOption?.ThingDef?.defName}). Could not find matching pawn kind");
			return null;
		}
		return new ScenPart_CustomAnimal
		{
			Count = equipment.Count,
			Gender = equipment.Gender.Value,
			KindDef = pawnKindDef
		};
	}

	public PawnKindDef FindPawnKindDefForRace(CustomizedEquipment equipment)
	{
		return DefDatabase<PawnKindDef>.AllDefs.Where((PawnKindDef k) => k.race == equipment.EquipmentOption.ThingDef).FirstOrDefault();
	}

	public void MarkCostsForRecalculation()
	{
		ViewState.CostCalculationDirtyFlag = true;
	}

	public void RecalculateCosts()
	{
		State.PointCost = CostCalculator.Calculate(State.Customizations.ColonyPawns, State.Customizations.Equipment);
	}

	public void LoadPreset(string filename)
	{
		PresetLoaderResult presetLoaderResult = PresetLoader.LoadFromFile(filename);
		Customizations customizations = presetLoaderResult?.Customizations;
		presetLoaderResult.Problems?.ForEach(delegate(PresetLoaderResult.Problem p)
		{
			if (p.Severity == 1)
			{
				Logger.Warning(p.Message);
			}
			else
			{
				Logger.Debug(p.Message);
			}
		});
		if (customizations == null)
		{
			Messages.Message("EdB.PC.Dialog.Preset.Error.FailedToLoad".Translate(filename), MessageTypeDefOf.ThreatBig);
			return;
		}
		if (customizations.ColonyPawns.Count < 1)
		{
			Messages.Message("EdB.PC.Dialog.Preset.Error.FailedToLoad".Translate(filename), MessageTypeDefOf.ThreatBig);
			Logger.Warning("Could not load preset because no colony pawns were loaded");
			return;
		}
		Messages.Message("EdB.PC.Dialog.Preset.Loaded".Translate(filename), MessageTypeDefOf.TaskCompletion);
		ManagerPawns.ClearPawns();
		foreach (CustomizedPawn allPawn in customizations.AllPawns)
		{
			allPawn.Pawn = ManagerPawns.Customizer.CreatePawnFromCustomizations(allPawn.Customizations);
			ManagerPawns.AddPawnToPawnList(allPawn);
		}
		ManagerEquipment.ClearEquipment();
		foreach (CustomizedEquipment item in customizations.Equipment)
		{
			ManagerEquipment.AddEquipment(item);
		}
		ManagerRelationships.Clear();
		State.Customizations.Relationships = customizations.Relationships;
		State.Customizations.ParentChildGroups = customizations.ParentChildGroups;
		PawnTabViewController.SelectPawn(presetLoaderResult.Customizations.ColonyPawns.FirstOrDefault());
	}

	public void SavePreset(string filename)
	{
		foreach (CustomizedPawn allPawn in State.Customizations.AllPawns)
		{
			ManagerPawns.MapCustomizationsForPawn(allPawn);
		}
		PresetSaver.SaveToFile(State, filename);
		Messages.Message("SavedAs".Translate(filename), MessageTypeDefOf.TaskCompletion);
	}
}
