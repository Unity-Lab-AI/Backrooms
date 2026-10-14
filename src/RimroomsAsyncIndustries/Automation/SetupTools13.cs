using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using Verse;

namespace RimroomsAsyncIndustries.Automation
{
    /// <summary>
    /// Guests (Hospitality). PLAYBOOK 4: "a guest room with guest beds ... sell processed goods". The guest bed is
    /// Hospitality's own class, `Hospitality.Building_GuestBed` (Hospitality (Continued), 1.7 Hospitality.dll), and its fee
    /// is the `RentalFee` property the bed's own price gizmo sets. Reached by name and reflection so this package never
    /// references Hospitality: with it absent the command says so and does nothing.
    ///   {"cmd":"guest_beds"}               list every guest bed and its nightly fee
    ///   {"cmd":"guest_beds","fee":"20"}    set every guest bed's fee (0 is free)
    /// </summary>
    internal static class SetupTools13
    {
        private const string GuestBedClass = "Hospitality.Building_GuestBed";

        public static string GuestBeds(Map map, Dictionary<string, string> a)
        {
            List<Building> beds = map.listerBuildings.allBuildingsColonist
                .Where(b => b.GetType().FullName == GuestBedClass).ToList();
            if (beds.Count == 0)
                return AppDomain.CurrentDomain.GetAssemblies().Any(x => x.GetType(GuestBedClass, false) != null)
                    ? "ok: no guest beds -- make a bed a guest bed with its Hospitality gizmo, in a guest room"
                    : "refused: Hospitality is not loaded";
            PropertyInfo fee = beds[0].GetType().GetProperty("RentalFee", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
            if (fee == null || fee.PropertyType != typeof(int) || !fee.CanRead)
                return "refused: this Hospitality's guest bed has no int RentalFee (version changed)";

            if (!a.TryGetValue("fee", out string fs) || string.IsNullOrWhiteSpace(fs))
                return "ok: " + beds.Count + " guest bed(s): " +
                       string.Join(", ", beds.Select(b => b.Position.x + "," + b.Position.z + " " + fee.GetValue(b, null) + " silver"));
            if (!int.TryParse(fs, NumberStyles.Integer, CultureInfo.InvariantCulture, out int want) || want < 0 || want > 500)
                return "refused: fee is a whole number of silver, 0-500";
            if (!fee.CanWrite) return "refused: RentalFee cannot be set on this Hospitality version";
            int changed = 0;
            foreach (Building b in beds)
            {
                if ((int)fee.GetValue(b, null) == want) continue;
                fee.SetValue(b, want, null);
                changed++;
            }
            return "ok: " + changed + " of " + beds.Count + " guest bed(s) now charge " + want + " silver a night";
        }
    }
}
