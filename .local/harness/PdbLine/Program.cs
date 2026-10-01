// Which source line is an IL offset in? Reads the portable PDB's sequence points.
//
// A RimWorld stack trace names the method and an IL offset -- `[0x001f8]` -- and nothing else.
// When a method throws the SAME exception message from two different places, the offset is the
// only thing that says which one fired, and reading the source cannot answer it. Guessing wrong
// costs the owner a launch.
//
// Also prints the assembly's MVID, because the trace carries one too -- that is what proves the
// PDB being read belongs to the assembly that actually threw.
//
//   dotnet run -- <assembly.dll> <TypeName> <MethodName> [ilOffsetHexOrDec ...]
using System;
using System.Collections.Immutable;
using System.IO;
using System.Linq;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;

internal static class Program
{
    private static int Main(string[] args)
    {
        if (args.Length < 3)
        {
            Console.Error.WriteLine("usage: PdbLine <assembly.dll> <TypeName> <MethodName> [ilOffset ...]");
            return 2;
        }

        string assemblyPath = Path.GetFullPath(args[0]);
        string typeName = args[1];
        string methodName = args[2];
        int[] offsets = args.Skip(3).Select(ParseOffset).ToArray();

        string pdbPath = Path.ChangeExtension(assemblyPath, ".pdb");
        if (!File.Exists(assemblyPath)) { Console.Error.WriteLine("no assembly: " + assemblyPath); return 2; }
        if (!File.Exists(pdbPath)) { Console.Error.WriteLine("no pdb: " + pdbPath); return 2; }

        using var peStream = File.OpenRead(assemblyPath);
        using var peReader = new PEReader(peStream);
        MetadataReader meta = peReader.GetMetadataReader();
        Console.WriteLine("assembly " + Path.GetFileName(assemblyPath));
        Console.WriteLine("MVID     " + meta.GetGuid(meta.GetModuleDefinition().Mvid).ToString());

        using var pdbStream = File.OpenRead(pdbPath);
        using MetadataReaderProvider provider = MetadataReaderProvider.FromPortablePdbStream(pdbStream);
        MetadataReader pdb = provider.GetMetadataReader();

        int found = 0;
        foreach (MethodDefinitionHandle handle in meta.MethodDefinitions)
        {
            MethodDefinition method = meta.GetMethodDefinition(handle);
            if (meta.GetString(method.Name) != methodName) { continue; }
            TypeDefinition declaring = meta.GetTypeDefinition(method.GetDeclaringType());
            string full = meta.GetString(declaring.Namespace) + "." + meta.GetString(declaring.Name);
            if (!full.EndsWith(typeName, StringComparison.Ordinal) &&
                meta.GetString(declaring.Name) != typeName) { continue; }

            MethodDebugInformation debug = pdb.GetMethodDebugInformation(handle.ToDebugInformationHandle());
            if (debug.SequencePointsBlob.IsNil) { continue; }
            ImmutableArray<SequencePoint> points = debug.GetSequencePoints()
                .Where(point => !point.IsHidden).ToImmutableArray();
            if (points.Length == 0) { continue; }

            found++;
            Console.WriteLine();
            Console.WriteLine(full + "." + methodName + "  (" + points.Length + " sequence points, IL 0x" +
                points[0].Offset.ToString("x") + "-0x" + points[points.Length - 1].Offset.ToString("x") + ")");

            if (offsets.Length == 0)
            {
                foreach (SequencePoint point in points)
                { Console.WriteLine("  IL 0x" + point.Offset.ToString("x4") + "  line " + point.StartLine); }
                continue;
            }

            foreach (int offset in offsets)
            {
                // The owning point is the last one at or before the offset: an IL offset falls
                // inside the statement that started at or before it.
                SequencePoint owner = default;
                bool any = false;
                foreach (SequencePoint point in points)
                {
                    if (point.Offset > offset) { break; }
                    owner = point;
                    any = true;
                }
                Console.WriteLine("  IL 0x" + offset.ToString("x4") + "  ->  " +
                    (any ? "line " + owner.StartLine + " (statement starts at IL 0x" +
                        owner.Offset.ToString("x4") + ")" : "before the first sequence point"));
            }
        }

        if (found == 0) { Console.Error.WriteLine("no method matched " + typeName + "." + methodName); return 1; }
        return 0;
    }

    private static int ParseOffset(string text)
    {
        text = text.Trim();
        if (text.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
        { return Convert.ToInt32(text.Substring(2), 16); }
        return int.Parse(text);
    }
}
