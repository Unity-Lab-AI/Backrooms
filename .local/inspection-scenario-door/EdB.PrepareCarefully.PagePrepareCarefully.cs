using System;
using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace EdB.PrepareCarefully;

public class PagePrepareCarefully : Page
{
	public delegate void PresetHandler(string name);

	public ControllerPage Controller { get; set; }

	public ModState State { get; set; }

	public ViewState ViewState { get; set; }

	public EquipmentDatabase EquipmentDatabase { get; set; }

	public bool LargeUI { get; set; }

	public override string PageTitle => "EdB.PC.Page.Title".Translate();

	private List<ITabView> TabViews { get; set; } = new List<ITabView>();

	private List<TabRecord> TabRecords { get; set; } = new List<TabRecord>();

	public TabViewPawns TabViewPawns { get; set; }

	public TabViewRelationships TabViewRelationships { get; set; }

	public TabViewEquipment TabViewEquipment { get; set; }

	public ITabView CurrentTab { get; set; }

	public DialogSavePreset Dialog { get; set; }

	public float? CostLabelWidth { get; set; }

	public override Vector2 InitialSize
	{
		get
		{
			Vector2 result = new Vector2(1350f, Page.StandardSize.y);
			if (LargeUI)
			{
				return result;
			}
			return Page.StandardSize;
		}
	}

	public event PresetHandler PresetLoaded;

	public event PresetHandler PresetSaved;

	public PagePrepareCarefully()
	{
		closeOnCancel = false;
		closeOnAccept = false;
		closeOnClickedOutside = false;
		doCloseButton = false;
		doCloseX = false;
		Dialog = new DialogSavePreset
		{
			Action = delegate(string name)
			{
				this.PresetSaved?.Invoke(name);
			}
		};
	}

	public void PostConstruction()
	{
		TabViews.Add(TabViewPawns);
		TabViews.Add(TabViewRelationships);
		TabViews.Add(TabViewEquipment);
		foreach (ITabView tabView in TabViews)
		{
			ITabView currentTab = tabView;
			TabRecord tabRecord = new TabRecord(currentTab.Name, delegate
			{
				if (CurrentTab != null)
				{
					CurrentTab.TabRecord.selected = false;
				}
				CurrentTab = currentTab;
				currentTab.TabRecord.selected = true;
			}, selected: false);
			currentTab.TabRecord = tabRecord;
			TabRecords.Add(tabRecord);
		}
		CurrentTab = TabViewPawns;
		TabViewPawns.TabRecord.selected = true;
	}

	public override void OnAcceptKeyPressed()
	{
	}

	public override void OnCancelKeyPressed()
	{
		ConfirmExit();
	}

	public override void Notify_ResolutionChanged()
	{
		Logger.Debug("Resolution changed to: [" + Screen.width + " x " + Screen.height + "]");
		base.Notify_ResolutionChanged();
	}

	public override void PreOpen()
	{
		base.PreOpen();
	}

	public override void DoWindowContents(Rect inRect)
	{
		if (ViewState.CostCalculationDirtyFlag)
		{
			Controller.RecalculateCosts();
			ViewState.CostCalculationDirtyFlag = false;
		}
		DrawPageTitle(inRect);
		Rect rect = GetMainRect(inRect).InsetBy(0f, -6f, 0f, 0f);
		Widgets.DrawMenuSection(rect);
		DrawTabViews(rect);
		DrawPresetButtons(inRect);
		DrawPoints(rect);
		DoNextBackButtons(inRect, "Start".Translate(), delegate
		{
			if (Controller.Validate())
			{
				ShowStartConfirmation();
			}
		}, delegate
		{
			ConfirmExit();
		});
		EquipmentDatabase.LoadFrame();
	}

	protected void DrawTabViews(Rect rect)
	{
		float num = 180f;
		float num2 = (float)TabRecords.Count * num;
		TabDrawer.DrawTabs(new Rect(rect.width * 0.5f - num2 * 0.5f, rect.y, num2, rect.height), TabRecords, 180f);
		Vector2 vector = new Vector2(16f, 16f);
		Rect rect2 = new Rect(rect.x + vector.x, rect.y + vector.y, rect.width - vector.x * 2f, rect.height - vector.y * 2f);
		CurrentTab.Draw(rect2);
	}

	public void DoNextBackButtons(Rect innerRect, string nextLabel, Action nextAct, Action backAct)
	{
		float y = innerRect.height - 38f;
		Text.Font = GameFont.Small;
		if (backAct != null && Widgets.ButtonText(new Rect(0f, y, Page.BottomButSize.x, Page.BottomButSize.y), "Back".Translate(), drawBackground: true, doMouseoverSound: false))
		{
			backAct();
		}
		if (nextAct != null && Widgets.ButtonText(new Rect(innerRect.width - Page.BottomButSize.x, y, Page.BottomButSize.x, Page.BottomButSize.y), nextLabel, drawBackground: true, doMouseoverSound: false))
		{
			nextAct();
		}
	}

	protected void DrawPresetButtons(Rect rect)
	{
		GUI.color = Color.white;
		float num = rect.width / 2f;
		float y = rect.height - 38f;
		float num2 = 150f;
		float num3 = 24f;
		if (Widgets.ButtonText(new Rect(num - num2 - num3 / 2f, y, num2, 38f), "EdB.PC.Page.Button.LoadPreset".Translate(), drawBackground: true, doMouseoverSound: false))
		{
			Find.WindowStack.Add(new DialogLoadPreset(delegate(string name)
			{
				this.PresetLoaded?.Invoke(name);
			}));
		}
		if (Widgets.ButtonText(new Rect(num + num3 / 2f, y, num2, 38f), "EdB.PC.Page.Button.SavePreset".Translate(), drawBackground: true, doMouseoverSound: false))
		{
			Dialog.ViewState = ViewState;
			Find.WindowStack.Add(Dialog);
		}
		GUI.color = Color.white;
	}

	protected void DrawPoints(Rect parentRect)
	{
		UtilityGUIState utilityGUIState = UtilityGUIState.Save();
		Text.Anchor = TextAnchor.UpperRight;
		GUI.color = Color.white;
		Text.Font = GameFont.Small;
		try
		{
			if (!CostLabelWidth.HasValue)
			{
				string text = int.MaxValue.ToString();
				string text2 = "EdB.PC.Page.Points.Spent".Translate(text);
				string text3 = "EdB.PC.Page.Points.Remaining".Translate(text);
				CostLabelWidth = Mathf.Max(Text.CalcSize(text2).x, Text.CalcSize(text3).x);
			}
			CostDetailsRefactored pointCost = State.PointCost;
			string label;
			if (ViewState.PointsEnabled)
			{
				int num = State.StartingPoints - (int)State.PointCost.total;
				if (num < 0)
				{
					GUI.color = Color.yellow;
				}
				else
				{
					GUI.color = Style.ColorText;
				}
				label = "EdB.PC.Page.Points.Remaining".Translate(num);
			}
			else
			{
				double total = pointCost.total;
				GUI.color = Style.ColorText;
				label = "EdB.PC.Page.Points.Spent".Translate(total);
			}
			Rect rect = new Rect(parentRect.width - CostLabelWidth.Value - 40f, 4f, CostLabelWidth.Value, 32f);
			Widgets.Label(rect, label);
			string tooltipText = "";
			tooltipText += "EdB.PC.Page.Points.ScenarioPoints".Translate(State.StartingPoints);
			tooltipText += "\n\n";
			foreach (PawnCostDetailsRefactored colonistDetail in pointCost.colonistDetails)
			{
				tooltipText += "EdB.PC.Page.Points.CostSummary.Colonist".Translate(colonistDetail.name, colonistDetail.total - colonistDetail.apparel - colonistDetail.possessions - colonistDetail.bionics) + "\n";
			}
			tooltipText += "\n" + "EdB.PC.Page.Points.CostSummary.Apparel".Translate(pointCost.colonistApparel) + "\n" + "EdB.PC.Page.Points.CostSummary.Possessions".Translate(pointCost.colonistPossessions) + "\n" + "EdB.PC.Page.Points.CostSummary.Implants".Translate(pointCost.colonistBionics) + "\n" + "EdB.PC.Page.Points.CostSummary.Equipment".Translate(pointCost.equipment) + "\n\n" + "EdB.PC.Page.Points.CostSummary.Total".Translate(pointCost.total);
			TooltipHandler.TipRegion(tip: new TipSignal(() => tooltipText, tooltipText.GetHashCode()), rect: rect);
			GUI.color = Color.white;
			Text.Anchor = TextAnchor.UpperLeft;
			Text.Font = GameFont.Small;
			if (!WidgetDropdown.Button(new Rect(rect.xMax + 8f, rect.yMin - 4f, 31f, 31f), "", drawBackground: true, doMouseoverSound: false, active: true))
			{
				return;
			}
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			if (ViewState.PointsEnabled)
			{
				list.Add(new FloatMenuOption("EdB.PC.Page.Points.DisablePoints".Translate(), delegate
				{
					ViewState.PointsEnabled = false;
				}));
			}
			else
			{
				list.Add(new FloatMenuOption("EdB.PC.Page.Points.UsePoints".Translate(), delegate
				{
					ViewState.PointsEnabled = true;
				}));
			}
			Find.WindowStack.Add(new FloatMenu(list, null));
		}
		finally
		{
			utilityGUIState.Restore();
		}
	}

	protected void ConfirmExit()
	{
		if (Controller.CancellingRequiresConfirmation())
		{
			Find.WindowStack.Add(new DialogConfirm("EdB.PC.Page.ConfirmExit".Translate(), delegate
			{
				Controller.CancelCustomizations();
				Close();
			}, destructive: true, null, showGoBack: true));
		}
		else
		{
			Close();
		}
	}

	protected void ShowStartConfirmation()
	{
		if (State.MissingWorkTypes != null && State.MissingWorkTypes.Count > 0)
		{
			StringBuilder stringBuilder = new StringBuilder();
			foreach (string missingWorkType in State.MissingWorkTypes)
			{
				if (stringBuilder.Length > 0)
				{
					stringBuilder.AppendLine();
				}
				stringBuilder.Append("  - " + missingWorkType.CapitalizeFirst());
			}
			string text = "ConfirmRequiredWorkTypeDisabledForEveryone".Translate(stringBuilder.ToString());
			Find.WindowStack.Add(Dialog_MessageBox.CreateConfirmation(text, delegate
			{
				Controller.StartGame();
			}));
		}
		else
		{
			Find.WindowStack.Add(new DialogConfirm("EdB.PC.Page.ConfirmStart".Translate(), delegate
			{
				Controller.StartGame();
			}, destructive: false, null, showGoBack: true));
		}
	}
}
