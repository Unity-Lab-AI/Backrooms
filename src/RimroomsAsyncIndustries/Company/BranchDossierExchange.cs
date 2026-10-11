using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Verse;

namespace RimroomsAsyncIndustries.Company
{
    /// <summary>One dossier this branch has written, kept so it can be written again unchanged.</summary>
    public sealed class DossierOutbound : IExposable
    {
        internal int sequence;
        internal string nonce;
        internal string digest;
        internal string fileName;
        internal string payload;
        internal int exportedTick;
        internal bool acknowledged;
        internal string acknowledgedBy;

        public int Sequence { get { return sequence; } }
        public string FileName { get { return fileName; } }
        public bool Acknowledged { get { return acknowledged; } }
        public string AcknowledgedBy { get { return acknowledgedBy; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref sequence, "rr_sequence");
            Scribe_Values.Look(ref nonce, "rr_nonce");
            Scribe_Values.Look(ref digest, "rr_digest");
            Scribe_Values.Look(ref fileName, "rr_fileName");
            Scribe_Values.Look(ref payload, "rr_payload");
            Scribe_Values.Look(ref exportedTick, "rr_exportedTick");
            Scribe_Values.Look(ref acknowledged, "rr_acknowledged");
            Scribe_Values.Look(ref acknowledgedBy, "rr_acknowledgedBy");
        }
    }

    /// <summary>A dossier another branch sent, accepted once and kept as read-only reference.</summary>
    public sealed class DossierInbound : IExposable
    {
        internal string sourceBranchId;
        internal string sourceCompany;
        internal int sequence;
        internal string nonce;
        internal string digest;
        internal int importedTick;
        internal long balanceUsd;
        internal int ledgerEntries;
        internal long ledgerNetUsd;
        internal int researchInsights;
        internal int casesOpen;
        internal int casesClosed;
        internal int evidenceHeld;
        internal int evidenceAnalyzed;
        internal int evidenceMissing;

        public string SourceCompany { get { return sourceCompany; } }
        public string SourceBranchId { get { return sourceBranchId; } }
        public int Sequence { get { return sequence; } }
        public long BalanceUsd { get { return balanceUsd; } }
        public int CasesOpen { get { return casesOpen; } }
        public int CasesClosed { get { return casesClosed; } }
        public int EvidenceHeld { get { return evidenceHeld; } }
        public int EvidenceAnalyzed { get { return evidenceAnalyzed; } }
        public int ResearchInsights { get { return researchInsights; } }

        public void ExposeData()
        {
            Scribe_Values.Look(ref sourceBranchId, "rr_sourceBranchId");
            Scribe_Values.Look(ref sourceCompany, "rr_sourceCompany");
            Scribe_Values.Look(ref sequence, "rr_sequence");
            Scribe_Values.Look(ref nonce, "rr_nonce");
            Scribe_Values.Look(ref digest, "rr_digest");
            Scribe_Values.Look(ref importedTick, "rr_importedTick");
            Scribe_Values.Look(ref balanceUsd, "rr_balanceUsd");
            Scribe_Values.Look(ref ledgerEntries, "rr_ledgerEntries");
            Scribe_Values.Look(ref ledgerNetUsd, "rr_ledgerNetUsd");
            Scribe_Values.Look(ref researchInsights, "rr_researchInsights");
            Scribe_Values.Look(ref casesOpen, "rr_casesOpen");
            Scribe_Values.Look(ref casesClosed, "rr_casesClosed");
            Scribe_Values.Look(ref evidenceHeld, "rr_evidenceHeld");
            Scribe_Values.Look(ref evidenceAnalyzed, "rr_evidenceAnalyzed");
            Scribe_Values.Look(ref evidenceMissing, "rr_evidenceMissing");
        }
    }

    /// <summary>A branch whose signing key this branch has accepted, pinned on first import.</summary>
    public sealed class DossierPeer : IExposable
    {
        internal string branchId;
        internal string publicKey;
        internal int lastSequence;

        public void ExposeData()
        {
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_Values.Look(ref publicKey, "rr_publicKey");
            Scribe_Values.Look(ref lastSequence, "rr_lastSequence");
        }
    }

    /// <summary>
    /// **Asynchronous branch-to-branch dossiers: a signed file, not a shared game.**
    ///
    /// Two co-op players each run their own company. What they can usefully hand each other
    /// between sessions is a statement of where a branch stands -- its books in summary, its
    /// cases, what evidence it holds and in what state -- and this is that, written as a file
    /// one player sends the other by any means they like.
    ///
    /// ## Why a file and not RimWorld Together
    ///
    /// RimWorld Together's client moves things and pawns between players through its transfer
    /// manifest (`RTClient.PacketManagers.PM_Transfers.AddToTransferManifest(Thing, int)`), and
    /// registers packet handlers by attribute inside its own assembly. It publishes no extension
    /// point for a custom payload: no registration call, no mod-data packet, nothing a second
    /// mod can hand a block of text to. A dossier is not a thing, and minting a thing to smuggle
    /// one through the manifest would depend on RimWorld Together scribing an unknown def's
    /// custom data intact, which nothing documents. So the provider route is **refused, with the
    /// reason**, and the local file is the supported route whether or not it is installed.
    ///
    /// ## What makes a file trustworthy enough
    ///
    /// * **Signed.** Each branch makes an RSA key pair the first time it exports, kept in its own
    ///   save. The dossier carries the public key and an RSA-SHA256 signature over its body. The
    ///   receiving branch pins that key to the sending branch id on first import and refuses any
    ///   later dossier from the same branch signed by a different key.
    /// * **Replay-proof.** Every dossier carries a per-branch sequence number and a random nonce.
    ///   An importer refuses a sequence it has already passed and a nonce it has already taken,
    ///   and refuses its own dossiers outright.
    /// * **Read-only on arrival.** Accepting a dossier records a summary beside this branch's
    ///   books. It never changes this branch's balance, research, cases or evidence. That is
    ///   what keeps it distinct from live shared control.
    ///
    /// ## Both-client recovery
    ///
    /// * **The sender loses the file:** every dossier is kept in the sender's save, and can be
    ///   written again byte for byte. Same sequence, same nonce, so a receiver that already has
    ///   it refuses the copy and one that does not accepts it.
    /// * **The sender reloads an older save:** the next sequence is the higher of the save's
    ///   counter and every dossier of this branch still on disk, so a rolled-back sender does not
    ///   reuse a number its partner has already seen.
    /// * **The receiver reloads an older save:** the import was never saved, so the same file is
    ///   accepted again.
    /// * **Did it arrive?** Accepting a dossier writes a signed receipt. Importing that receipt on
    ///   the sending side marks the dossier acknowledged.
    /// </summary>
    public sealed class RimroomsDossierExchangeComponent : GameComponent
    {
        public const int CurrentSchemaVersion = 1;
        public const int MaxFileBytes = 64 * 1024;
        private const string Magic = "RIMROOMS-DOSSIER";
        private const string ReceiptMagic = "RIMROOMS-RECEIPT";
        private const string FormatVersion = "1";
        private const int RimWorldTogetherRow = 196;
        private const int MaxInbound = 64;
        private const int MaxOutbound = 32;

        private int schemaVersion = CurrentSchemaVersion;
        private string branchId;
        private string privateKey;
        private int nextSequence = 1;
        private List<DossierOutbound> outbound = new List<DossierOutbound>();
        private List<DossierInbound> inbound = new List<DossierInbound>();
        private List<DossierPeer> peers = new List<DossierPeer>();
        private List<string> takenNonces = new List<string>();
        private string faultKey;

        public RimroomsDossierExchangeComponent(Game game) { }

        public IReadOnlyList<DossierOutbound> Outbound { get { return outbound; } }
        public IReadOnlyList<DossierInbound> Inbound { get { return inbound; } }
        public string FaultKey { get { return faultKey; } }

        /// <summary>Where dossiers and receipts are written and read, beside the save folder.</summary>
        public static string Folder
        { get { return Path.Combine(GenFilePaths.SaveDataFolderPath, "RimroomsDossiers"); } }

        private static RimroomsCampaignComponent Campaign
        { get { return Current.Game == null ? null : Current.Game.GetComponent<RimroomsCampaignComponent>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref schemaVersion, "rr_dossierSchema", 1, true);
            Scribe_Values.Look(ref branchId, "rr_branchId");
            Scribe_Values.Look(ref privateKey, "rr_signingKey");
            Scribe_Values.Look(ref nextSequence, "rr_nextSequence", 1);
            Scribe_Collections.Look(ref outbound, "rr_outbound", LookMode.Deep);
            Scribe_Collections.Look(ref inbound, "rr_inbound", LookMode.Deep);
            Scribe_Collections.Look(ref peers, "rr_peers", LookMode.Deep);
            Scribe_Collections.Look(ref takenNonces, "rr_takenNonces", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                outbound = outbound ?? new List<DossierOutbound>();
                inbound = inbound ?? new List<DossierInbound>();
                peers = peers ?? new List<DossierPeer>();
                takenNonces = takenNonces ?? new List<string>();
                outbound.RemoveAll(entry => entry == null || string.IsNullOrEmpty(entry.payload));
                inbound.RemoveAll(entry => entry == null);
                peers.RemoveAll(entry => entry == null || string.IsNullOrEmpty(entry.branchId));
                faultKey = schemaVersion != CurrentSchemaVersion ? "RR_Dossier_UnsupportedSchema"
                    : nextSequence < 1 ? "RR_Dossier_InvalidSave" : null;
            }
        }

        /// <summary>
        /// The provider route, always refused with the reason: RimWorld Together exposes no
        /// payload path a second mod can use. Absent, it says so instead.
        /// </summary>
        public static CompanyActionResult SendThroughProvider()
        {
            return CompanyActionResult.Refused(Core.InstalledIntegrations.ActiveRow(RimWorldTogetherRow)
                ? "RR_Dossier_ProviderNoPath" : "RR_Dossier_ProviderAbsent");
        }

        private CompanyActionResult CheckBranch(RimroomsCampaignComponent campaign)
        {
            if (faultKey != null) { return CompanyActionResult.Refused(faultKey); }
            if (campaign == null || !campaign.CanOperate) { return CompanyActionResult.Refused("RR_Dossier_BranchUnavailable"); }
            if (!string.IsNullOrEmpty(branchId) && branchId != campaign.BranchId)
            { return CompanyActionResult.Refused("RR_Dossier_BranchUnavailable"); }
            return CompanyActionResult.Applied();
        }

        private RSACryptoServiceProvider SigningKey()
        {
            var rsa = new RSACryptoServiceProvider(2048) { PersistKeyInCsp = false };
            if (string.IsNullOrEmpty(privateKey)) { privateKey = rsa.ToXmlString(true); }
            else { rsa.FromXmlString(privateKey); }
            return rsa;
        }

        /// <summary>Writes a new dossier for this branch. Returns the file name in the result's key on success.</summary>
        public CompanyActionResult Export(out string writtenFile)
        {
            writtenFile = null;
            RimroomsCampaignComponent campaign = Campaign;
            CompanyActionResult branch = CheckBranch(campaign);
            if (!branch.Success) { return branch; }
            try
            {
                Directory.CreateDirectory(Folder);
                branchId = campaign.BranchId;
                int sequence = Math.Max(nextSequence, HighestSequenceOnDisk(branchId) + 1);
                string nonce = Guid.NewGuid().ToString("N");
                string body = BuildBody(campaign, sequence, nonce);
                string payload;
                using (RSACryptoServiceProvider rsa = SigningKey())
                {
                    byte[] signature = rsa.SignData(Encoding.UTF8.GetBytes(body), new SHA256Managed());
                    payload = body + "publicKey\t" + rsa.ToXmlString(false) + "\n" +
                        "signature\t" + Convert.ToBase64String(signature) + "\n";
                }
                string fileName = "dossier-" + SafeName(branchId) + "-" + sequence.ToString(CultureInfo.InvariantCulture) + ".txt";
                File.WriteAllText(Path.Combine(Folder, fileName), payload, new UTF8Encoding(false));
                nextSequence = sequence + 1;
                outbound.Add(new DossierOutbound
                {
                    sequence = sequence, nonce = nonce, digest = Digest(body), fileName = fileName,
                    payload = payload, exportedTick = Find.TickManager.TicksGame,
                });
                while (outbound.Count > MaxOutbound) { outbound.RemoveAt(0); }
                writtenFile = fileName;
                return CompanyActionResult.Applied();
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms] Dossier export failed: " + exception.Message);
                return CompanyActionResult.Refused("RR_Dossier_WriteFailed");
            }
        }

        /// <summary>Writes a kept dossier again, byte for byte, for a sender who lost the file.</summary>
        public CompanyActionResult Rewrite(DossierOutbound entry)
        {
            if (entry == null || !outbound.Contains(entry)) { return CompanyActionResult.Refused("RR_Dossier_NotFound"); }
            try
            {
                Directory.CreateDirectory(Folder);
                File.WriteAllText(Path.Combine(Folder, entry.fileName), entry.payload, new UTF8Encoding(false));
                return CompanyActionResult.Applied();
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms] Dossier rewrite failed: " + exception.Message);
                return CompanyActionResult.Refused("RR_Dossier_WriteFailed");
            }
        }

        /// <summary>Dossier and receipt files waiting in the folder that are not this branch's own dossiers.</summary>
        public List<string> PendingFiles()
        {
            var files = new List<string>();
            try
            {
                if (!Directory.Exists(Folder)) { return files; }
                string ours = Campaign?.BranchId ?? branchId;
                string own = string.IsNullOrEmpty(ours) ? null : "dossier-" + SafeName(ours) + "-";
                foreach (string path in Directory.GetFiles(Folder, "*.txt"))
                {
                    string name = Path.GetFileName(path);
                    if (own != null && name.StartsWith(own, StringComparison.Ordinal)) { continue; }
                    if (name.StartsWith("receipt-", StringComparison.Ordinal) && !string.IsNullOrEmpty(ours) &&
                        !name.StartsWith("receipt-" + SafeName(ours) + "-", StringComparison.Ordinal)) { continue; }
                    files.Add(name);
                }
                files.Sort(StringComparer.Ordinal);
            }
            catch (Exception exception) { Log.Warning("[Rimrooms] Dossier folder unreadable: " + exception.Message); }
            return files;
        }

        /// <summary>Accepts one dossier or receipt file by name. Every refusal leaves this branch unchanged.</summary>
        public CompanyActionResult Import(string fileName)
        {
            RimroomsCampaignComponent campaign = Campaign;
            CompanyActionResult branch = CheckBranch(campaign);
            if (!branch.Success) { return branch; }
            if (string.IsNullOrEmpty(fileName) || fileName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)
            { return CompanyActionResult.Refused("RR_Dossier_NotFound"); }
            string text;
            try
            {
                string path = Path.Combine(Folder, fileName);
                var info = new FileInfo(path);
                if (!info.Exists) { return CompanyActionResult.Refused("RR_Dossier_NotFound"); }
                if (info.Length > MaxFileBytes) { return CompanyActionResult.Refused("RR_Dossier_Malformed"); }
                text = File.ReadAllText(path, Encoding.UTF8);
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms] Dossier read failed: " + exception.Message);
                return CompanyActionResult.Refused("RR_Dossier_NotFound");
            }
            if (!TryParse(text, out Dictionary<string, string> fields, out string body)) { return CompanyActionResult.Refused("RR_Dossier_Malformed"); }
            if (!VerifySignature(fields, body)) { return CompanyActionResult.Refused("RR_Dossier_BadSignature"); }
            string magic = Field(fields, "magic");
            if (magic == ReceiptMagic) { return AcceptReceipt(campaign, fields); }
            if (magic != Magic) { return CompanyActionResult.Refused("RR_Dossier_Malformed"); }
            return AcceptDossier(campaign, fields, body);
        }

        private CompanyActionResult AcceptDossier(RimroomsCampaignComponent campaign, Dictionary<string, string> fields, string body)
        {
            string source = Field(fields, "branch");
            string nonce = Field(fields, "nonce");
            if (!TryInt(fields, "sequence", out int sequence) || sequence < 1 ||
                string.IsNullOrEmpty(source) || string.IsNullOrEmpty(nonce))
            { return CompanyActionResult.Refused("RR_Dossier_Malformed"); }
            if (source == campaign.BranchId) { return CompanyActionResult.Refused("RR_Dossier_OwnDossier"); }
            if (takenNonces.Contains(nonce)) { return CompanyActionResult.Refused("RR_Dossier_Replay"); }
            string key = Field(fields, "publicKey");
            DossierPeer peer = peers.Find(entry => entry.branchId == source);
            if (peer != null && peer.publicKey != key) { return CompanyActionResult.Refused("RR_Dossier_KeyChanged"); }
            if (peer != null && sequence <= peer.lastSequence) { return CompanyActionResult.Refused("RR_Dossier_Replay"); }
            var record = new DossierInbound
            {
                sourceBranchId = source, sourceCompany = Field(fields, "company") ?? "",
                sequence = sequence, nonce = nonce, digest = Digest(body),
                importedTick = Find.TickManager.TicksGame,
            };
            if (!TryLong(fields, "balanceUsd", out record.balanceUsd) || !TryInt(fields, "ledgerEntries", out record.ledgerEntries) ||
                !TryLong(fields, "ledgerNetUsd", out record.ledgerNetUsd) || !TryInt(fields, "researchInsights", out record.researchInsights) ||
                !TryInt(fields, "casesOpen", out record.casesOpen) || !TryInt(fields, "casesClosed", out record.casesClosed) ||
                !TryInt(fields, "evidenceHeld", out record.evidenceHeld) || !TryInt(fields, "evidenceAnalyzed", out record.evidenceAnalyzed) ||
                !TryInt(fields, "evidenceMissing", out record.evidenceMissing))
            { return CompanyActionResult.Refused("RR_Dossier_Malformed"); }
            // The receipt is written before anything is recorded, so a failed write leaves the
            // dossier importable again rather than accepted without an acknowledgement.
            if (!WriteReceipt(campaign, source, sequence, record.digest)) { return CompanyActionResult.Refused("RR_Dossier_WriteFailed"); }
            if (peer == null) { peers.Add(new DossierPeer { branchId = source, publicKey = key, lastSequence = sequence }); }
            else { peer.lastSequence = sequence; }
            takenNonces.Add(nonce);
            inbound.Add(record);
            while (inbound.Count > MaxInbound) { inbound.RemoveAt(0); }
            return CompanyActionResult.Applied();
        }

        private CompanyActionResult AcceptReceipt(RimroomsCampaignComponent campaign, Dictionary<string, string> fields)
        {
            if (Field(fields, "forBranch") != campaign.BranchId) { return CompanyActionResult.Refused("RR_Dossier_ReceiptNotOurs"); }
            if (!TryInt(fields, "sequence", out int sequence)) { return CompanyActionResult.Refused("RR_Dossier_Malformed"); }
            DossierOutbound entry = outbound.Find(item => item.sequence == sequence && item.digest == Field(fields, "digest"));
            if (entry == null) { return CompanyActionResult.Refused("RR_Dossier_ReceiptUnknown"); }
            if (entry.acknowledged) { return CompanyActionResult.Existing(); }
            entry.acknowledged = true;
            entry.acknowledgedBy = Field(fields, "company") ?? "";
            return CompanyActionResult.Applied();
        }

        private bool WriteReceipt(RimroomsCampaignComponent campaign, string source, int sequence, string digest)
        {
            try
            {
                var builder = new StringBuilder();
                Line(builder, "magic", ReceiptMagic);
                Line(builder, "format", FormatVersion);
                Line(builder, "branch", campaign.BranchId);
                Line(builder, "company", campaign.CompanyName);
                Line(builder, "forBranch", source);
                Line(builder, "sequence", sequence.ToString(CultureInfo.InvariantCulture));
                Line(builder, "digest", digest);
                string body = builder.ToString();
                string payload;
                using (RSACryptoServiceProvider rsa = SigningKey())
                {
                    byte[] signature = rsa.SignData(Encoding.UTF8.GetBytes(body), new SHA256Managed());
                    payload = body + "publicKey\t" + rsa.ToXmlString(false) + "\n" +
                        "signature\t" + Convert.ToBase64String(signature) + "\n";
                }
                Directory.CreateDirectory(Folder);
                string name = "receipt-" + SafeName(source) + "-" + sequence.ToString(CultureInfo.InvariantCulture) +
                    "-from-" + SafeName(campaign.BranchId) + ".txt";
                File.WriteAllText(Path.Combine(Folder, name), payload, new UTF8Encoding(false));
                return true;
            }
            catch (Exception exception)
            {
                Log.Warning("[Rimrooms] Dossier receipt write failed: " + exception.Message);
                return false;
            }
        }

        private static string BuildBody(RimroomsCampaignComponent campaign, int sequence, string nonce)
        {
            long net = 0;
            IReadOnlyList<LedgerEntry> ledger = campaign.Ledger;
            for (int index = 0; index < ledger.Count; index++) { if (ledger[index] != null) { net += ledger[index].AmountUsd; } }
            int open = 0, closed = 0;
            foreach (CaseRecord record in campaign.Cases) { if (record == null) { continue; } if (record.Closed) { closed++; } else { open++; } }
            int held = 0, analyzed = 0, missing = 0;
            foreach (EvidenceRecord record in campaign.Evidence)
            {
                if (record == null) { continue; }
                if (record.Status == EvidenceStatus.Missing) { missing++; continue; }
                if (record.Status == EvidenceStatus.Analyzed) { analyzed++; }
                if (record.Item != null && !record.Item.Destroyed) { held++; }
            }
            var builder = new StringBuilder();
            Line(builder, "magic", Magic);
            Line(builder, "format", FormatVersion);
            Line(builder, "branch", campaign.BranchId);
            Line(builder, "company", campaign.CompanyName);
            Line(builder, "sequence", sequence.ToString(CultureInfo.InvariantCulture));
            Line(builder, "nonce", nonce);
            Line(builder, "tick", Find.TickManager.TicksGame.ToString(CultureInfo.InvariantCulture));
            Line(builder, "balanceUsd", campaign.BalanceUsd.ToString(CultureInfo.InvariantCulture));
            Line(builder, "ledgerEntries", ledger.Count.ToString(CultureInfo.InvariantCulture));
            Line(builder, "ledgerNetUsd", net.ToString(CultureInfo.InvariantCulture));
            Line(builder, "researchInsights", campaign.ResearchInsights.ToString(CultureInfo.InvariantCulture));
            Line(builder, "casesOpen", open.ToString(CultureInfo.InvariantCulture));
            Line(builder, "casesClosed", closed.ToString(CultureInfo.InvariantCulture));
            Line(builder, "evidenceHeld", held.ToString(CultureInfo.InvariantCulture));
            Line(builder, "evidenceAnalyzed", analyzed.ToString(CultureInfo.InvariantCulture));
            Line(builder, "evidenceMissing", missing.ToString(CultureInfo.InvariantCulture));
            return builder.ToString();
        }

        private static void Line(StringBuilder builder, string key, string value)
        {
            string clean = (value ?? "").Replace('\t', ' ').Replace('\r', ' ').Replace('\n', ' ');
            builder.Append(key).Append('\t').Append(clean).Append('\n');
        }

        /// <summary>Splits a file into fields; the signed body is every line before the public key.</summary>
        private static bool TryParse(string text, out Dictionary<string, string> fields, out string body)
        {
            fields = new Dictionary<string, string>(StringComparer.Ordinal);
            body = null;
            if (string.IsNullOrEmpty(text)) { return false; }
            int keyAt = text.IndexOf("\npublicKey\t", StringComparison.Ordinal);
            if (keyAt < 0) { return false; }
            body = text.Substring(0, keyAt + 1);
            foreach (string raw in text.Split('\n'))
            {
                if (raw.Length == 0) { continue; }
                int tab = raw.IndexOf('\t');
                if (tab <= 0) { return false; }
                string key = raw.Substring(0, tab);
                if (fields.ContainsKey(key)) { return false; }
                fields[key] = raw.Substring(tab + 1);
            }
            return Field(fields, "format") == FormatVersion && fields.ContainsKey("signature");
        }

        private static bool VerifySignature(Dictionary<string, string> fields, string body)
        {
            try
            {
                using (var rsa = new RSACryptoServiceProvider { PersistKeyInCsp = false })
                {
                    rsa.FromXmlString(Field(fields, "publicKey"));
                    byte[] signature = Convert.FromBase64String(Field(fields, "signature"));
                    return rsa.VerifyData(Encoding.UTF8.GetBytes(body), new SHA256Managed(), signature);
                }
            }
            catch (Exception) { return false; }
        }

        private int HighestSequenceOnDisk(string branch)
        {
            int highest = 0;
            string prefix = "dossier-" + SafeName(branch) + "-";
            foreach (string path in Directory.GetFiles(Folder, prefix + "*.txt"))
            {
                string name = Path.GetFileNameWithoutExtension(path);
                if (int.TryParse(name.Substring(prefix.Length), NumberStyles.None, CultureInfo.InvariantCulture, out int value))
                { highest = Math.Max(highest, value); }
            }
            return highest;
        }

        private static string Field(Dictionary<string, string> fields, string key)
        { return fields.TryGetValue(key, out string value) ? value : null; }

        private static bool TryInt(Dictionary<string, string> fields, string key, out int value)
        { return int.TryParse(Field(fields, key), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out value); }

        private static bool TryLong(Dictionary<string, string> fields, string key, out long value)
        { return long.TryParse(Field(fields, key), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out value); }

        private static string Digest(string body)
        {
            using (var sha = new SHA256Managed())
            { return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(body))).Replace("-", ""); }
        }

        private static string SafeName(string value)
        {
            var builder = new StringBuilder();
            foreach (char character in value ?? "")
            { builder.Append(char.IsLetterOrDigit(character) ? character : '_'); }
            return builder.ToString();
        }
    }
}
