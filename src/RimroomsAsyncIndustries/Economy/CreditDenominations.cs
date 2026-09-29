using System;
using System.Collections.Generic;

namespace RimroomsAsyncIndustries.Economy
{
    /// <summary>
    /// The denomination ladder for company bearer bonds, and the rule for paying somebody in
    /// the fewest pieces of paper.
    ///
    /// **Owner direction, 2026-09-29, verbatim:** *"they need to go up to values of 1 million
    /// like 10, 100, 1000, 10000 ... ect ect and a production bench with buills for makeing the
    /// differnt sizes and u are always payed in the highest values with least amount of bonds"*,
    /// then immediately after: *"yeah keep teriing it then dont stop at 1 million"*.
    ///
    /// So the ladder runs **10 to one quadrillion** — every power of ten from 10^1 to 10^15.
    /// A million is a rung in the middle of it rather than the top.
    ///
    /// ## Why it goes that high, and why it stops where it does
    ///
    /// The parent corporation is recorded as operating at multi-trillion-dollar scale, and a
    /// ladder topping out at a million would need **a million pieces of paper to represent one
    /// trillion** — which is not a vault, it is a warehouse. Stopping at 10^15 keeps a
    /// multi-trillion sum to three or four bonds while staying far inside <see cref="long"/>,
    /// whose ceiling is about 9.2 × 10^18. Even a hoard of thousands of top bonds cannot
    /// overflow a total.
    ///
    /// ## Every rung is exactly ten of the one below
    ///
    /// That is what makes the production chain *simple and easy* as asked, rather than a
    /// conversion table: ten of anything is one of the next thing, in both directions, with no
    /// arithmetic for the player to do and no awkward remainder.
    /// </summary>
    public static class CreditDenominations
    {
        /// <summary>Lowest exponent on the ladder. 10^1 = 10 credits.</summary>
        public const int LowestExponent = 1;

        /// <summary>Highest exponent on the ladder. 10^15 = one quadrillion credits.</summary>
        public const int HighestExponent = 15;

        private static readonly long[] values = BuildValues();

        private static long[] BuildValues()
        {
            var built = new long[HighestExponent - LowestExponent + 1];
            long value = 1L;
            for (int exponent = 1; exponent <= HighestExponent; exponent++)
            {
                value *= 10L;
                if (exponent >= LowestExponent) { built[exponent - LowestExponent] = value; }
            }
            return built;
        }

        /// <summary>Every denomination, ascending. 10, 100, 1,000 ... 1,000,000,000,000,000.</summary>
        public static IReadOnlyList<long> Values { get { return values; } }

        /// <summary>The smallest denomination. Anything below it cannot be held as paper.</summary>
        public static long Smallest { get { return values[0]; } }

        /// <summary>The largest denomination.</summary>
        public static long Largest { get { return values[values.Length - 1]; } }

        /// <summary>Whether a face value sits exactly on the ladder.</summary>
        public static bool IsDenomination(long value)
        {
            for (int index = 0; index < values.Length; index++)
            {
                if (values[index] == value) { return true; }
            }
            return false;
        }

        /// <summary>The exponent of a denomination, or -1 if the value is not on the ladder.</summary>
        public static int ExponentOf(long value)
        {
            for (int index = 0; index < values.Length; index++)
            {
                if (values[index] == value) { return index + LowestExponent; }
            }
            return -1;
        }

        /// <summary>The denomination for an exponent, or 0 if it is off the ladder.</summary>
        public static long ValueForExponent(int exponent)
        {
            int index = exponent - LowestExponent;
            return index < 0 || index >= values.Length ? 0L : values[index];
        }

        /// <summary>
        /// Breaks an amount into the **fewest possible bonds, largest first** — the owner's
        /// *"u are always payed in the highest values with least amount of bonds"*.
        ///
        /// Greedy is provably optimal here because every rung is an exact multiple of every
        /// rung below it, so there is no case where taking a smaller note first would end up
        /// using fewer notes overall. That is the same reason it works for real currency and
        /// the reason a power-of-ten ladder was worth insisting on.
        /// </summary>
        /// <param name="amount">Credits to pay out. Negative is treated as nothing.</param>
        /// <param name="remainder">
        /// What could not be represented — always less than <see cref="Smallest"/>. The caller
        /// decides what to do with it; this never silently rounds a player's money away.
        /// </param>
        /// <returns>Denomination value to count, largest first.</returns>
        public static List<KeyValuePair<long, int>> Decompose(long amount, out long remainder)
        {
            var result = new List<KeyValuePair<long, int>>();
            remainder = amount <= 0L ? 0L : amount;
            if (amount <= 0L) { return result; }

            for (int index = values.Length - 1; index >= 0; index--)
            {
                long denomination = values[index];
                if (remainder < denomination) { continue; }
                long count = remainder / denomination;
                // A single payout is never allowed to be an unbounded pile of paper. Anything
                // beyond this is a sign the ladder needs another rung, not that the player
                // should receive two billion items.
                if (count > int.MaxValue) { count = int.MaxValue; }
                result.Add(new KeyValuePair<long, int>(denomination, (int)count));
                remainder -= count * denomination;
            }
            return result;
        }

        /// <summary>Total face value of a decomposition, for checking against the input.</summary>
        public static long TotalOf(List<KeyValuePair<long, int>> decomposition)
        {
            long total = 0L;
            if (decomposition == null) { return total; }
            for (int index = 0; index < decomposition.Count; index++)
            {
                total += decomposition[index].Key * decomposition[index].Value;
            }
            return total;
        }

        /// <summary>
        /// A short human name for a denomination — "1 million", "10 trillion". Built from the
        /// exponent rather than a lookup table so a new rung needs no new text.
        /// </summary>
        public static string ShortName(long value)
        {
            int exponent = ExponentOf(value);
            if (exponent < 0) { return value.ToString("N0"); }
            string[] scales = { "", "thousand", "million", "billion", "trillion", "quadrillion" };
            int scale = exponent / 3;
            int leading = (int)Math.Pow(10, exponent % 3);
            if (scale <= 0 || scale >= scales.Length) { return value.ToString("N0"); }
            return leading.ToString("N0") + " " + scales[scale];
        }
    }
}
