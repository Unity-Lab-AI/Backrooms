using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace EdB.PrepareCarefully;

public class Mod
{
	public static readonly Version MinimumGameVersion = new Version(1, 5, 0);

	private static Mod instance = new Mod();

	public static Mod Instance
	{
		get
		{
			if (instance == null)
			{
				instance = new Mod();
			}
			return instance;
		}
	}

	public ModState State { get; set; }

	public static void ClearInstance()
	{
		instance = null;
	}

	public void Clear()
	{
		instance = null;
	}

	public void Start(Page_ConfigureStartingPawns configureStartingPawnsPage)
	{
		ReflectionCache.Instance.Initialize();
		ModState modState = (State = new ModState
		{
			OriginalPage = configureStartingPawnsPage
		});
		EquipmentDatabase equipmentDatabase = new EquipmentDatabase();
		Logger.Debug("Initializing alien races");
		ProviderAlienRaces providerAlienRaces = new ProviderAlienRaces();
		Logger.Debug("Initializing hair");
		ProviderHair providerHair = new ProviderHair
		{
			ProviderAlienRaces = providerAlienRaces
		};
		Logger.Debug("Initializing beards");
		ProviderBeards providerBeards = new ProviderBeards
		{
			ProviderAlienRaces = providerAlienRaces
		};
		Logger.Debug("Initializing body types");
		ProviderBodyTypes providerBodyTypes = new ProviderBodyTypes
		{
			ProviderAlienRaces = providerAlienRaces
		};
		Logger.Debug("Initializing head types");
		ProviderHeadTypes providerHeadTypes = new ProviderHeadTypes
		{
			ProviderAlienRaces = providerAlienRaces
		};
		Logger.Debug("Initializing face tattoos");
		ProviderFaceTattoos providerFaceTattoos = new ProviderFaceTattoos
		{
			ProviderAlienRaces = providerAlienRaces
		};
		Logger.Debug("Initializing body tattoos");
		ProviderBodyTattoos providerBodyTattoos = new ProviderBodyTattoos
		{
			ProviderAlienRaces = providerAlienRaces
		};
		Logger.Debug("Initializing age limits");
		ProviderAgeLimits providerAgeLimits = new ProviderAgeLimits();
		Logger.Debug("Initializing pawn kinds");
		ProviderPawnKinds providerPawnKinds = new ProviderPawnKinds();
		Logger.Debug("Initializing factions");
		ProviderFactions providerFactions = new ProviderFactions();
		Logger.Debug("Initializing backstories");
		ProviderBackstories providerBackstories = new ProviderBackstories
		{
			ProviderFactions = providerFactions
		};
		Logger.Debug("Initializing pawn layers");
		ProviderPawnLayers providerPawnLayers = new ProviderPawnLayers
		{
			ProviderAlienRaces = providerAlienRaces,
			ProviderHair = providerHair,
			ProviderBeards = providerBeards,
			ProviderBodyTypes = providerBodyTypes,
			ProviderHeadTypes = providerHeadTypes,
			ProviderBodyTattoos = providerBodyTattoos,
			ProviderFaceTattoos = providerFaceTattoos
		};
		Logger.Debug("Initializing titles");
		ProviderTitles providerTitles = new ProviderTitles();
		Logger.Debug("Initializing traits");
		ProviderTraits providerTraits = new ProviderTraits();
		Logger.Debug("Initializing health options");
		ProviderHealthOptions providerHealthOptions = new ProviderHealthOptions();
		Logger.Debug("Initializing equipment");
		ProviderEquipment providerEquipment = new ProviderEquipment
		{
			EquipmentDatabase = equipmentDatabase
		};
		providerEquipment.PostConstruction();
		Logger.Debug("Initializing passions");
		ProviderPassions providerPassions = new ProviderPassions();
		providerPassions.PostConstruct();
		Logger.Debug("Providers initialized");
		AgeModifier ageModifier = new AgeModifier();
		ViewState viewState = new ViewState();
		MapperPawnToCustomizations pawnToCustomizationsMapper = new MapperPawnToCustomizations
		{
			ProviderHealth = providerHealthOptions,
			ProviderAlienRaces = providerAlienRaces
		};
		PawnCustomizer pawnCustomizer = new PawnCustomizer();
		PawnLoaderV3 pawnLoaderV = new PawnLoaderV3
		{
			EquipmentDatabase = equipmentDatabase,
			ProviderHealthOptions = providerHealthOptions
		};
		PawnLoaderV5 pawnLoaderV2 = new PawnLoaderV5
		{
			ProviderHealthOptions = providerHealthOptions,
			ProviderPassions = providerPassions
		};
		PawnLoader pawnLoader = new PawnLoader
		{
			PawnLoaderV3 = pawnLoaderV,
			PawnLoaderV5 = pawnLoaderV2
		};
		RelationshipDefinitionHelper relationshipDefinitionHelper = new RelationshipDefinitionHelper();
		relationshipDefinitionHelper.PostConstruct();
		ManagerRelationships managerRelationships = new ManagerRelationships
		{
			State = modState,
			RelationshipDefinitionHelper = relationshipDefinitionHelper
		};
		PresetLoaderV3 presetLoaderV = new PresetLoaderV3
		{
			PawnLoaderV3 = pawnLoaderV,
			EquipmentDatabase = equipmentDatabase,
			ManagerRelationships = managerRelationships
		};
		PresetLoaderV5 presetLoaderV2 = new PresetLoaderV5
		{
			PawnLoaderV5 = pawnLoaderV2,
			EquipmentDatabase = equipmentDatabase,
			ManagerRelationships = managerRelationships
		};
		PresetLoader presetLoader = new PresetLoader
		{
			PresetLoaderV3 = presetLoaderV,
			PresetLoaderV5 = presetLoaderV2
		};
		PawnSaver pawnSaver = new PawnSaver
		{
			ProviderHealthOptions = providerHealthOptions,
			ProviderPassions = providerPassions
		};
		PresetSaver presetSaver = new PresetSaver
		{
			PawnSaver = pawnSaver
		};
		CostCalculator costCalculator = new CostCalculator
		{
			ProviderHealthOptions = providerHealthOptions
		};
		ManagerPawns pawnManager = new ManagerPawns
		{
			State = modState,
			PawnToCustomizationsMapper = pawnToCustomizationsMapper,
			Customizer = pawnCustomizer,
			ProviderAgeLimits = providerAgeLimits,
			ProviderAlienRaces = providerAlienRaces,
			ProviderBackstories = providerBackstories,
			ProviderHeadTypes = providerHeadTypes,
			ProviderBodyTypes = providerBodyTypes,
			ProviderFactions = providerFactions,
			ProviderHealthOptions = providerHealthOptions,
			AgeModifier = ageModifier,
			EquipmentDatabase = equipmentDatabase,
			PawnLoader = pawnLoader,
			PawnSaver = pawnSaver
		};
		ManagerEquipment managerEquipment = new ManagerEquipment
		{
			State = modState,
			EquipmentDatabase = equipmentDatabase
		};
		pawnManager.InitializeStateFromStartingPawns();
		managerRelationships.InitializeWithPawns(modState.Customizations.AllPawns);
		managerEquipment.InitializeStateFromScenarioAndStartingPawns();
		State.StartingPoints = (int)costCalculator.Calculate(State.Customizations.ColonyPawns, State.Customizations.Equipment).total;
		ControllerTabViewPawns controllerTabViewPawns = new ControllerTabViewPawns
		{
			State = modState,
			ViewState = viewState,
			Customizer = pawnCustomizer,
			PawnManager = pawnManager,
			RelationshipManager = managerRelationships,
			ProviderPassions = providerPassions
		};
		ControllerTabViewRelationships controllerTabViewRelationships = new ControllerTabViewRelationships
		{
			State = modState,
			ViewState = viewState,
			RelationshipManager = managerRelationships
		};
		ControllerTabViewEquipment controllerTabViewEquipment = new ControllerTabViewEquipment
		{
			State = modState,
			ViewState = viewState,
			EquipmentManager = managerEquipment
		};
		ControllerPage controllerPage = new ControllerPage
		{
			State = modState,
			ViewState = viewState,
			PawnTabViewController = controllerTabViewPawns,
			RelationshipTabViewController = controllerTabViewRelationships,
			CostCalculator = costCalculator,
			PawnCustomizer = pawnCustomizer,
			ManagerPawns = pawnManager,
			ManagerEquipment = managerEquipment,
			ManagerRelationships = managerRelationships,
			PresetLoader = presetLoader,
			PresetSaver = presetSaver
		};
		bool largeUI = controllerPage.UseLargeUI();
		controllerPage.PostConstruct();
		PanelColonyPawnListRefactored panelColonyPawnListRefactored = new PanelColonyPawnListRefactored
		{
			State = modState,
			ViewState = viewState,
			ProviderPawnKinds = providerPawnKinds
		};
		PanelColonyPawnListMinimized panelColonyPawnListMinimized = new PanelColonyPawnListMinimized
		{
			State = modState,
			ViewState = viewState
		};
		PanelWorldPawnList panelWorldPawnList = new PanelWorldPawnList
		{
			State = modState,
			ViewState = viewState,
			ProviderPawnKinds = providerPawnKinds
		};
		PanelWorldPawnListMinimized panelWorldPawnListMinimized = new PanelWorldPawnListMinimized
		{
			State = modState,
			ViewState = viewState
		};
		PanelRandomize panelRandomize = new PanelRandomize
		{
			State = modState,
			ViewState = viewState
		};
		PanelName panelName = new PanelName
		{
			State = modState,
			ViewState = viewState
		};
		PanelSaveCharacter panelSaveCharacter = new PanelSaveCharacter
		{
			ViewState = viewState
		};
		PanelAppearance panelAppearance = new PanelAppearance
		{
			State = modState,
			ViewState = viewState,
			ProviderPawnLayers = providerPawnLayers,
			ProviderAlienRaces = providerAlienRaces,
			PawnController = controllerTabViewPawns
		};
		PanelApparel panelApparel = new PanelApparel
		{
			State = modState,
			ViewState = viewState,
			ProviderEquipmentTypes = providerEquipment
		};
		PanelPossessions panelPossessions = new PanelPossessions
		{
			State = modState,
			ViewState = viewState
		};
		PanelAbilitiesRefactored panelAbilitiesRefactored = new PanelAbilitiesRefactored
		{
			State = modState,
			ViewState = viewState
		};
		panelAbilitiesRefactored.PostConstruct();
		PanelIdeo panelIdeo = new PanelIdeo
		{
			State = modState,
			ViewState = viewState
		};
		PanelXenotype panelXenotype = new PanelXenotype
		{
			State = modState,
			ViewState = viewState
		};
		PanelAgeRefactored panelAgeRefactored = new PanelAgeRefactored
		{
			State = modState,
			ViewState = viewState,
			ProviderAgeLimits = providerAgeLimits
		};
		PanelBackstory panelBackstory = new PanelBackstory
		{
			State = modState,
			ViewState = viewState,
			ProviderBackstories = providerBackstories
		};
		panelBackstory.PostConstruct();
		PanelTitles panelTitles = new PanelTitles
		{
			State = modState,
			ViewState = viewState,
			ProviderTitles = providerTitles
		};
		PanelTraits panelTraits = new PanelTraits
		{
			State = modState,
			ViewState = viewState,
			ProviderTraits = providerTraits
		};
		PanelHealth panelHealth = new PanelHealth
		{
			State = modState,
			ViewState = viewState,
			ProviderHealth = providerHealthOptions
		};
		PanelSkills panelSkills = new PanelSkills
		{
			State = modState,
			ViewState = viewState,
			ProviderPassions = providerPassions
		};
		PanelIncapableOf panelIncapableOf = new PanelIncapableOf
		{
			State = modState,
			ViewState = viewState
		};
		PanelRelationshipsParentChild panelRelationshipsParentChild = new PanelRelationshipsParentChild
		{
			State = modState,
			ViewState = viewState,
			RelationshipManager = managerRelationships,
			Controller = controllerTabViewRelationships
		};
		PanelRelationshipsOther panelRelationshipsOther = new PanelRelationshipsOther
		{
			State = modState,
			ViewState = viewState,
			RelationshipManager = managerRelationships
		};
		PanelEquipmentAvailable panelEquipmentAvailable = new PanelEquipmentAvailable
		{
			State = modState,
			ViewState = viewState,
			ProviderEquipment = providerEquipment,
			CostCalculator = costCalculator
		};
		panelEquipmentAvailable.PostConstruct();
		PanelEquipmentSelected panelEquipmentSelected = new PanelEquipmentSelected
		{
			State = modState,
			ViewState = viewState,
			EquipmentDatabase = equipmentDatabase
		};
		TabViewPawns tabViewPawns = new TabViewPawns
		{
			State = modState,
			ViewState = viewState,
			PanelColonyPawns = panelColonyPawnListRefactored,
			PanelColonyPawnsMinimized = panelColonyPawnListMinimized,
			PanelWorldPawns = panelWorldPawnList,
			PanelWorldPawnsMinimized = panelWorldPawnListMinimized,
			PanelRandomize = panelRandomize,
			PanelName = panelName,
			PanelSaveCharacter = panelSaveCharacter,
			PanelAppearance = panelAppearance,
			PanelApparel = panelApparel,
			PanelPossessions = panelPossessions,
			PanelAge = panelAgeRefactored,
			PanelBackstory = panelBackstory,
			PanelTraits = panelTraits,
			PanelHealth = panelHealth,
			PanelSkills = panelSkills,
			PanelIncapableOf = panelIncapableOf,
			PanelTitles = panelTitles,
			PanelAbilities = panelAbilitiesRefactored,
			PanelIdeo = panelIdeo,
			PanelXenotype = panelXenotype,
			LargeUI = largeUI
		};
		tabViewPawns.PostConstruction();
		TabViewRelationships tabViewRelationships = new TabViewRelationships
		{
			PanelRelationshipsParentChild = panelRelationshipsParentChild,
			PanelRelationshipsOther = panelRelationshipsOther
		};
		TabViewEquipment tabViewEquipment = new TabViewEquipment
		{
			PanelAvailable = panelEquipmentAvailable,
			PanelSelected = panelEquipmentSelected
		};
		PagePrepareCarefully pagePrepareCarefully = new PagePrepareCarefully
		{
			State = modState,
			ViewState = viewState,
			Controller = controllerPage,
			TabViewPawns = tabViewPawns,
			TabViewRelationships = tabViewRelationships,
			TabViewEquipment = tabViewEquipment,
			LargeUI = largeUI,
			EquipmentDatabase = equipmentDatabase
		};
		pagePrepareCarefully.PostConstruction();
		pawnManager.CostAffected += controllerPage.MarkCostsForRecalculation;
		managerEquipment.CostAffected += controllerPage.MarkCostsForRecalculation;
		panelColonyPawnListMinimized.Maximizing += controllerTabViewPawns.MaximizeColonyPawnList;
		panelColonyPawnListRefactored.PawnSelected += controllerTabViewPawns.SelectPawn;
		panelColonyPawnListRefactored.PawnDeleted += controllerTabViewPawns.DeletePawn;
		panelColonyPawnListRefactored.AddingPawn += controllerTabViewPawns.AddColonyPawn;
		panelColonyPawnListRefactored.PawnSwapped += controllerTabViewPawns.MoveColonyPawnToWorldPawnList;
		panelColonyPawnListRefactored.AddingPawnWithPawnKind += controllerTabViewPawns.AddPawnWithPawnKind;
		panelColonyPawnListRefactored.PawnLoaded += controllerTabViewPawns.LoadColonyPawn;
		panelWorldPawnListMinimized.Maximizing += controllerTabViewPawns.MaximizeWorldPawnList;
		panelWorldPawnList.PawnSelected += controllerTabViewPawns.SelectPawn;
		panelWorldPawnList.PawnDeleted += controllerTabViewPawns.DeletePawn;
		panelWorldPawnList.AddingPawn += controllerTabViewPawns.AddWorldPawn;
		panelWorldPawnList.PawnSwapped += controllerTabViewPawns.MoveWorldPawnToColonyPawnList;
		panelWorldPawnList.AddingPawnWithPawnKind += controllerTabViewPawns.AddPawnWithPawnKind;
		panelWorldPawnList.PawnLoaded += controllerTabViewPawns.LoadWorldPawn;
		panelRandomize.RandomizeAllClicked += controllerTabViewPawns.RandomizeCurrentPawn;
		panelName.FirstNameUpdated += controllerTabViewPawns.UpdateFirstName;
		panelName.NickNameUpdated += controllerTabViewPawns.UpdateNickName;
		panelName.LastNameUpdated += controllerTabViewPawns.UpdateLastName;
		panelName.NameRandomized += controllerTabViewPawns.RandomizeName;
		panelSaveCharacter.CharacterSaved += controllerTabViewPawns.SavePawn;
		panelBackstory.BackstoryUpdated += controllerTabViewPawns.UpdateBackstoryHandler;
		panelBackstory.RandomizeButtonClicked += controllerTabViewPawns.RandomizeBackstory;
		panelBackstory.FavoriteColorUpdated += controllerTabViewPawns.UpdateFavoriteColor;
		panelSkills.PassionButtonClicked += controllerTabViewPawns.UpdateSkillPassion;
		panelSkills.IncrementSkillButtonClicked += controllerTabViewPawns.IncrementSkill;
		panelSkills.DecrementSkillButtonClicked += controllerTabViewPawns.DecrementSkill;
		panelSkills.SkillBarClicked += controllerTabViewPawns.SetSkillLevel;
		panelSkills.ClearSkillsButtonClicked += controllerTabViewPawns.ClearSkillsAndPassions;
		panelSkills.ResetSkillsButtonClicked += controllerTabViewPawns.ResetAddedSkillLevelsAndPassions;
		panelTraits.TraitAdded += controllerTabViewPawns.AddTrait;
		panelTraits.TraitRemoved += controllerTabViewPawns.RemoveTrait;
		panelTraits.TraitsRandomized += controllerTabViewPawns.RandomizeTraits;
		panelTraits.TraitUpdated += controllerTabViewPawns.UpdateTrait;
		panelTraits.TraitsSet += controllerTabViewPawns.SetTraits;
		panelAppearance.GenderUpdated += controllerTabViewPawns.UpdateGender;
		panelAppearance.SkinColorUpdated += controllerTabViewPawns.UpdateSkinColor;
		panelAppearance.RandomizeAppearance += controllerTabViewPawns.RandomizeAppearance;
		panelApparel.ApparelRemoved += controllerTabViewPawns.RemoveApparel;
		panelApparel.ApparelAdded += controllerTabViewPawns.AddApparel;
		panelApparel.ApparelReplaced += controllerTabViewPawns.SetApparel;
		panelAgeRefactored.BiologicalAgeUpdated += controllerTabViewPawns.UpdateBiologicalAge;
		panelAgeRefactored.ChronologicalAgeUpdated += controllerTabViewPawns.UpdateChronologicalAge;
		panelHealth.InjuryAdded += controllerTabViewPawns.AddInjury;
		panelHealth.HediffsRemoved += controllerTabViewPawns.RemoveHediffs;
		panelHealth.ImplantsUpdated += controllerTabViewPawns.UpdateImplants;
		panelAbilitiesRefactored.AbilitiesSet += controllerTabViewPawns.SetAbilities;
		panelAbilitiesRefactored.AbilityRemoved += controllerTabViewPawns.RemoveAbility;
		panelIdeo.IdeoUpdated += controllerTabViewPawns.UpdateIdeo;
		panelIdeo.IdeoRandomized += controllerTabViewPawns.RandomizeIdeo;
		panelIdeo.CertaintyUpdated += controllerTabViewPawns.UpdateCertainty;
		panelRelationshipsOther.RelationshipAdded += controllerTabViewRelationships.AddRelationship;
		panelRelationshipsOther.RelationshipRemoved += controllerTabViewRelationships.RemoveRelationship;
		panelRelationshipsParentChild.GroupAdded += controllerTabViewRelationships.AddParentChildGroup;
		panelRelationshipsParentChild.ChildAddedToGroup += controllerTabViewRelationships.AddChildToParentChildGroup;
		panelRelationshipsParentChild.ParentAddedToGroup += controllerTabViewRelationships.AddParentToParentChildGroup;
		panelRelationshipsParentChild.ChildRemovedFromGroup += controllerTabViewRelationships.RemoveChildFromParentChildGroup;
		panelRelationshipsParentChild.ParentRemovedFromGroup += controllerTabViewRelationships.RemoveParentFromParentChildGroup;
		panelEquipmentAvailable.EquipmentAdded += controllerTabViewEquipment.AddEquipment;
		panelEquipmentAvailable.EquipmentAdded += panelEquipmentSelected.EquipmentAdded;
		panelEquipmentSelected.EquipmentCountUpdated += controllerTabViewEquipment.UpdateEquipmentCount;
		panelEquipmentSelected.EquipmentRemoved += controllerTabViewEquipment.RemoveEquipment;
		panelEquipmentSelected.PossessionRemoved += controllerTabViewPawns.RemovePossession;
		panelEquipmentSelected.PossessionCountUpdated += controllerTabViewPawns.UpdatePossessionCount;
		pagePrepareCarefully.PresetLoaded += controllerPage.LoadPreset;
		pagePrepareCarefully.PresetSaved += controllerPage.SavePreset;
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerHair), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			pawnManager.UpdateHair(customizedPawn, (option as PawnLayerOptionHair).HairDef);
		});
		controllerTabViewPawns.RegisterPawnLayerColorUpdateHandler(typeof(PawnLayerHair), delegate(PawnLayer layer, CustomizedPawn customizedPawn, Color color)
		{
			pawnManager.UpdateHairColor(customizedPawn, color);
		});
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerHead), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			pawnManager.UpdateHeadType(customizedPawn, (option as PawnLayerOptionHead).HeadType);
		});
		controllerTabViewPawns.RegisterPawnLayerColorUpdateHandler(typeof(PawnLayerHead), delegate(PawnLayer layer, CustomizedPawn customizedPawn, Color color)
		{
			pawnManager.UpdateSkinColor(customizedPawn, color);
		});
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerBody), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			pawnManager.UpdateBodyType(customizedPawn, (option as PawnLayerOptionBody).BodyTypeDef);
		});
		controllerTabViewPawns.RegisterPawnLayerColorUpdateHandler(typeof(PawnLayerBody), delegate(PawnLayer layer, CustomizedPawn customizedPawn, Color color)
		{
			pawnManager.UpdateSkinColor(customizedPawn, color);
		});
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerBeard), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			pawnManager.UpdateBeard(customizedPawn, (option as PawnLayerOptionBeard).BeardDef);
		});
		controllerTabViewPawns.RegisterPawnLayerColorUpdateHandler(typeof(PawnLayerBeard), delegate(PawnLayer layer, CustomizedPawn customizedPawn, Color color)
		{
			pawnManager.UpdateHairColor(customizedPawn, color);
		});
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerFaceTattoo), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			pawnManager.UpdateFaceTattoo(customizedPawn, (option as PawnLayerOptionTattoo).TattooDef);
		});
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerBodyTattoo), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			pawnManager.UpdateBodyTattoo(customizedPawn, (option as PawnLayerOptionTattoo).TattooDef);
		});
		controllerTabViewPawns.RegisterPawnLayerOptionUpdateHandler(typeof(PawnLayerAlienAddon), delegate(PawnLayer layer, CustomizedPawn customizedPawn, PawnLayerOption option)
		{
			PawnLayerOptionAlienAddon pawnLayerOptionAlienAddon = option as PawnLayerOptionAlienAddon;
			PawnLayerAlienAddon pawnLayerAlienAddon = layer as PawnLayerAlienAddon;
			pawnManager.UpdateAlienAddon(customizedPawn, pawnLayerAlienAddon.AlienAddon, pawnLayerOptionAlienAddon.Index);
		});
		controllerTabViewPawns.RegisterPawnLayerColorUpdateHandler(typeof(PawnLayerAlienAddon), delegate(PawnLayer layer, CustomizedPawn customizedPawn, Color color)
		{
			PawnLayerAlienAddon pawnLayerAlienAddon = layer as PawnLayerAlienAddon;
			if (pawnLayerAlienAddon.Skin)
			{
				pawnManager.UpdateSkinColor(customizedPawn, color);
			}
			else if (pawnLayerAlienAddon.Hair)
			{
				pawnManager.UpdateHairColor(customizedPawn, color);
			}
		});
		Find.WindowStack.Add(pagePrepareCarefully);
	}

	public void RestoreScenarioParts()
	{
		if (State?.OriginalScenarioParts != null)
		{
			try
			{
				ReflectionUtil.SetFieldValue(Find.Scenario, "parts", State.OriginalScenarioParts);
			}
			finally
			{
				State.OriginalScenarioParts = null;
			}
		}
	}
}
