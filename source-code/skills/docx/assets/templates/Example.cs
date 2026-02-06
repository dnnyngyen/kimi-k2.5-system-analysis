// Example.cs - Designer-grade complete document example
// Demonstrates OpenXML SDK technical implementation for professional documents
// Learn structure and code, adjust colors and style based on scenario

using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using DW = DocumentFormat.OpenXml.Drawing.Wordprocessing;
using A = DocumentFormat.OpenXml.Drawing;
using PIC = DocumentFormat.OpenXml.Drawing.Pictures;
using C = DocumentFormat.OpenXml.Drawing.Charts;

namespace KimiDocx;

public static class Example
{
    // ============================================================================
    // Color Scheme - Morandi Nordic Style: Low saturation, elegant
    // ============================================================================
    private static class Colors
    {
        // Morandi primary colors
        public const string Primary = "7C9885";       // Sage green - main headings
        public const string Secondary = "8B9DC3";     // Gray blue - secondary
        public const string Accent = "9CAF88";        // Grass green - accent

        // Text color scale
        public const string Dark = "2d3a35";          // Dark text (greenish gray)
        public const string Mid = "5a6b62";           // Secondary text
        public const string Light = "8a9a90";         // Helper text

        // Background/Border
        public const string Border = "d8e0dc";
        public const string TableHeader = "f0f4f2";
    }

    // ============================================================================
    // A4 Size Constants
    // ============================================================================
    private const int A4WidthTwips = 11906;      // 210mm
    private const int A4HeightTwips = 16838;     // 297mm
    private const long A4WidthEmu = 7560000L;    // 210mm * 36000
    private const long A4HeightEmu = 10692000L;  // 297mm * 36000

    public static void Generate(string outputPath, string bgDir)
    {
        using var doc = WordprocessingDocument.Create(outputPath, WordprocessingDocumentType.Document);
        var mainPart = doc.AddMainDocumentPart();
        mainPart.Document = new Document(new Body());
        var body = mainPart.Document.Body!;

        // Add styles
        AddStyles(mainPart);

        // Add numbering definitions
        AddNumbering(mainPart);

        // Add image relationships
        var coverImageId = AddImage(mainPart, Path.Combine(bgDir, "cover_bg.png"));
        var bodyImageId = AddImage(mainPart, Path.Combine(bgDir, "body_bg.png"));
        var backcoverImageId = AddImage(mainPart, Path.Combine(bgDir, "backcover_bg.png"));

        // ========== Cover Section ==========
        AddCoverSection(body, coverImageId);

        // ========== Table of Contents Section ==========
        AddTocSection(body, bodyImageId, mainPart);

        // ========== Body Section ==========
        AddContentSection(doc, body, bodyImageId, mainPart, bgDir);

        // ========== Back Cover Section ==========
        AddBackcoverSection(body, backcoverImageId);

        // Set update fields on open
        SetUpdateFieldsOnOpen(mainPart);

        doc.Save();
        Console.WriteLine($"Generated: {outputPath}");
    }

    // ============================================================================
    // Add Styles
    // ============================================================================
    private static void AddStyles(MainDocumentPart mainPart)
    {
        var stylesPart = mainPart.AddNewPart<StyleDefinitionsPart>();
        stylesPart.Styles = new Styles();

        // Normal style
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "Normal" },
            new StyleParagraphProperties(
                new SpacingBetweenLines { After = "200", Line = "312", LineRule = LineSpacingRuleValues.Auto }
            ),
            new StyleRunProperties(
                new RunFonts { Ascii = "Calibri", HighAnsi = "Calibri", EastAsia = "Microsoft YaHei" },
                new FontSize { Val = "21" },
                new Color { Val = Colors.Dark }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Normal", Default = true });

        // Heading1
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "heading 1" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepNext(),
                new KeepLines(),
                new SpacingBetweenLines { Before = "600", After = "240", Line = "240", LineRule = LineSpacingRuleValues.Auto },
                new OutlineLevel { Val = 0 }
            ),
            new StyleRunProperties(
                new Bold(),
                new Color { Val = Colors.Primary },  // Morandi green
                new FontSize { Val = "36" }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Heading1" });

        // Heading2
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "heading 2" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepNext(),
                new KeepLines(),
                new SpacingBetweenLines { Before = "400", After = "160" },
                new OutlineLevel { Val = 1 }
            ),
            new StyleRunProperties(
                new Bold(),
                new Color { Val = Colors.Dark },
                new FontSize { Val = "28" }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Heading2" });

        // Heading3
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "heading 3" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepNext(),
                new KeepLines(),
                new SpacingBetweenLines { Before = "280", After = "120" },
                new OutlineLevel { Val = 2 }
            ),
            new StyleRunProperties(
                new Bold(),
                new Color { Val = Colors.Mid },
                new FontSize { Val = "24" }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Heading3" });

        // Caption - more prominent
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "Caption" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepLines(),
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { Before = "60", After = "400" }
            ),
            new StyleRunProperties(
                new Color { Val = Colors.Mid },
                new FontSize { Val = "20" }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Caption" });

        // TOC1
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "toc 1" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new Tabs(new TabStop { Val = TabStopValues.Right, Leader = TabStopLeaderCharValues.Dot, Position = 9350 }),
                new SpacingBetweenLines { Before = "200", After = "60" }
            ),
            new StyleRunProperties(
                new Bold(),
                new Color { Val = Colors.Dark }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "TOC1" });

        // TOC2
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "toc 2" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new Tabs(new TabStop { Val = TabStopValues.Right, Leader = TabStopLeaderCharValues.Dot, Position = 9350 }),
                new SpacingBetweenLines { Before = "60", After = "60" },
                new Indentation { Left = "360" }
            ),
            new StyleRunProperties(
                new Color { Val = Colors.Mid }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "TOC2" });
    }

    // ============================================================================
    // Add Numbering
    // ============================================================================
    private static void AddNumbering(MainDocumentPart mainPart)
    {
        var numberingPart = mainPart.AddNewPart<NumberingDefinitionsPart>();
        numberingPart.Numbering = CreateBasicNumbering();
    }

    // ============================================================================
    // Add Image
    // ============================================================================
    private static string AddImage(MainDocumentPart mainPart, string imagePath)
    {
        var imagePart = mainPart.AddImagePart(ImagePartType.Png);
        using var stream = new FileStream(imagePath, FileMode.Open);
        imagePart.FeedData(stream);
        return mainPart.GetIdOfPart(imagePart);
    }

    // ============================================================================
    // Create Floating Background Image
    // ============================================================================
    private static Drawing CreateFloatingBackground(string imageId, uint docPrId, string name)
    {
        return new Drawing(
            new DW.Anchor(
                new DW.SimplePosition { X = 0, Y = 0 },
                new DW.HorizontalPosition(new DW.PositionOffset("0"))
                { RelativeFrom = DW.HorizontalRelativePositionValues.Page },
                new DW.VerticalPosition(new DW.PositionOffset("0"))
                { RelativeFrom = DW.VerticalRelativePositionValues.Page },
                new DW.Extent { Cx = A4WidthEmu, Cy = A4HeightEmu },
                new DW.EffectExtent { LeftEdge = 0, TopEdge = 0, RightEdge = 0, BottomEdge = 0 },
                new DW.WrapNone(),
                new DW.DocProperties { Id = docPrId, Name = name },
                new DW.NonVisualGraphicFrameDrawingProperties(
                    new A.GraphicFrameLocks { NoChangeAspect = true }
                ),
                new A.Graphic(
                    new A.GraphicData(
                        new PIC.Picture(
                            new PIC.NonVisualPictureProperties(
                                new PIC.NonVisualDrawingProperties { Id = 0, Name = $"{name}.png" },
                                new PIC.NonVisualPictureDrawingProperties()
                            ),
                            new PIC.BlipFill(
                                new A.Blip { Embed = imageId },
                                new A.Stretch(new A.FillRectangle())
                            ),
                            new PIC.ShapeProperties(
                                new A.Transform2D(
                                    new A.Offset { X = 0, Y = 0 },
                                    new A.Extents { Cx = A4WidthEmu, Cy = A4HeightEmu }
                                ),
                                new A.PresetGeometry { Preset = A.ShapeTypeValues.Rectangle }
                            )
                        )
                    )
                    { Uri = "http://schemas.openxmlformats.org/drawingml/2006/picture" }
                )
            )
            {
                DistanceFromTop = 0,
                DistanceFromBottom = 0,
                DistanceFromLeft = 0,
                DistanceFromRight = 0,
                SimplePos = false,
                RelativeHeight = 251658240,
                BehindDoc = true,  // Key: behind text
                Locked = false,
                LayoutInCell = true,
                AllowOverlap = true
            }
        );
    }

    // ============================================================================
    // Insert Inline Image (matplotlib charts, etc.) - Auto-read dimensions, maintain ratio
    // ============================================================================
    private static void AddInlineImage(Body body, MainDocumentPart mainPart, string imagePath, string altText, uint docPrId, int maxWidthCm = 15)
    {
        // Add image
        var imagePart = mainPart.AddImagePart(ImagePartType.Png);
        byte[] imageBytes = File.ReadAllBytes(imagePath);
        using (var ms = new MemoryStream(imageBytes))
            imagePart.FeedData(ms);
        var imageId = mainPart.GetIdOfPart(imagePart);

        // Read actual image dimensions
        int imgWidth, imgHeight;
        using (var ms = new MemoryStream(imageBytes))
        {
            // PNG header: 8 bytes signature, then IHDR chunk
            // Width at offset 16-19, Height at offset 20-23 (big-endian)
            ms.Seek(16, SeekOrigin.Begin);
            byte[] widthBytes = new byte[4];
            byte[] heightBytes = new byte[4];
            ms.Read(widthBytes, 0, 4);
            ms.Read(heightBytes, 0, 4);
            // Big-endian to int
            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(widthBytes);
                Array.Reverse(heightBytes);
            }
            imgWidth = BitConverter.ToInt32(widthBytes, 0);
            imgHeight = BitConverter.ToInt32(heightBytes, 0);
        }

        // Calculate display dimensions - maintain ratio, limit max width
        long maxWidthEmu = maxWidthCm * 360000L;  // 1cm = 360000 EMU
        double ratio = (double)imgHeight / imgWidth;
        long cx = maxWidthEmu;
        long cy = (long)(cx * ratio);

        var drawing = new Drawing(
            new DW.Inline(
                new DW.Extent { Cx = cx, Cy = cy },
                new DW.EffectExtent { LeftEdge = 0, TopEdge = 0, RightEdge = 0, BottomEdge = 0 },
                new DW.DocProperties { Id = docPrId, Name = altText },
                new DW.NonVisualGraphicFrameDrawingProperties(
                    new A.GraphicFrameLocks { NoChangeAspect = true }
                ),
                new A.Graphic(
                    new A.GraphicData(
                        new PIC.Picture(
                            new PIC.NonVisualPictureProperties(
                                new PIC.NonVisualDrawingProperties { Id = 0, Name = $"{altText}.png" },
                                new PIC.NonVisualPictureDrawingProperties()
                            ),
                            new PIC.BlipFill(
                                new A.Blip { Embed = imageId },
                                new A.Stretch(new A.FillRectangle())
                            ),
                            new PIC.ShapeProperties(
                                new A.Transform2D(
                                    new A.Offset { X = 0, Y = 0 },
                                    new A.Extents { Cx = cx, Cy = cy }
                                ),
                                new A.PresetGeometry { Preset = A.ShapeTypeValues.Rectangle }
                            )
                        )
                    )
                    { Uri = "http://schemas.openxmlformats.org/drawingml/2006/picture" }
                )
            )
            { DistanceFromTop = 0, DistanceFromBottom = 0, DistanceFromLeft = 0, DistanceFromRight = 0 }
        );

        // KeepNext ensures chart and caption stay on same page
        body.Append(new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { Before = "200", After = "80" }
            ),
            new Run(drawing)
        ));
    }

    // ============================================================================
    // Cover Section - Minimalist Design
    // ============================================================================
    private static void AddCoverSection(Body body, string coverImageId)
    {
        // Background image
        body.Append(new Paragraph(new Run(CreateFloatingBackground(coverImageId, 1, "CoverBackground"))));

        // Large whitespace - title at lower-middle of page
        body.Append(new Paragraph(
            new ParagraphProperties(new SpacingBetweenLines { Before = "6000" }),
            new Run()
        ));

        // Main title - large, left-aligned, with margins
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Left },
                new Indentation { Left = "1200", Right = "1200" },
                new SpacingBetweenLines { After = "400" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "96" },  // 48pt
                    new Color { Val = Colors.Dark }
                ),
                new Text("Project Proposal")
            )
        ));

        // Subtitle - smaller, primary color
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Left },
                new Indentation { Left = "1200", Right = "1200" },
                new SpacingBetweenLines { After = "3000" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "24" },
                    new Color { Val = Colors.Primary },
                    new Spacing { Val = 40 }
                ),
                new Text("Strategic Business Initiative")
            )
        ));

        // Bottom info - minimalist
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Left },
                new Indentation { Left = "1200" },
                new SpacingBetweenLines { After = "120" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "20" },
                    new Color { Val = Colors.Light }
                ),
                new Text("[Company Name]")
            )
        ));

        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Left },
                new Indentation { Left = "1200" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "18" },
                    new Color { Val = Colors.Light }
                ),
                new Text("2024.12")
            )
        ));

        // Cover section properties
        body.Append(new Paragraph(
            new ParagraphProperties(
                new SectionProperties(
                    new SectionType { Val = SectionMarkValues.NextPage },
                    new PageSize { Width = (UInt32Value)(uint)A4WidthTwips, Height = (UInt32Value)(uint)A4HeightTwips },
                    new PageMargin { Top = 0, Right = 0, Bottom = 0, Left = 0, Header = 0, Footer = 0 }
                )
            )
        ));
    }

    // ============================================================================
    // Table of Contents Section
    // ============================================================================
    private static void AddTocSection(Body body, string bodyImageId, MainDocumentPart mainPart)
    {
        // TOC title
        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Heading1" }),
            new BookmarkStart { Id = "0", Name = "_Toc000" },
            new Run(new Text("Table of Contents")),
            new BookmarkEnd { Id = "0" }
        ));

        // Hint text
        body.Append(new Paragraph(
            new ParagraphProperties(new SpacingBetweenLines { After = "300" }),
            new Run(
                new RunProperties(
                    new Color { Val = Colors.Light },
                    new FontSize { Val = "18" }
                ),
                new Text("Right-click the TOC and select \u201cUpdate Field\u201d to refresh page numbers")
            )
        ));

        // TOC field begin
        body.Append(new Paragraph(
            new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }),
            new Run(new FieldCode(" TOC \\o \"1-3\" \\h \\z \\u ") { Space = SpaceProcessingModeValues.Preserve }),
            new Run(new FieldChar { FieldCharType = FieldCharValues.Separate })
        ));

        // Placeholder TOC entries
        string[,] tocEntries = {
            { "Executive Summary", "1", "3" },
            { "Project Background", "1", "4" },
            { "Industry Overview", "2", "4" },
            { "Customer Pain Points", "2", "5" },
            { "Proposed Solution", "1", "6" },
            { "Core Modules", "2", "6" },
            { "Project Timeline", "1", "8" }
        };

        foreach (var i in Enumerable.Range(0, tocEntries.GetLength(0)))
        {
            var level = tocEntries[i, 1];
            var styleId = level == "1" ? "TOC1" : "TOC2";

            body.Append(new Paragraph(
                new ParagraphProperties(new ParagraphStyleId { Val = styleId }),
                new Run(new Text(tocEntries[i, 0])),
                new Run(new TabChar()),
                new Run(new Text(tocEntries[i, 2]))
            ));
        }

        // TOC field end
        body.Append(new Paragraph(
            new Run(new FieldChar { FieldCharType = FieldCharValues.End })
        ));

        // TOC section properties (NextPage auto page break, no manual page break needed)
        body.Append(new Paragraph(
            new ParagraphProperties(
                new SectionProperties(
                    new SectionType { Val = SectionMarkValues.NextPage },
                    new PageSize { Width = (UInt32Value)(uint)A4WidthTwips, Height = (UInt32Value)(uint)A4HeightTwips },
                    new PageMargin { Top = 1800, Right = 1440, Bottom = 1440, Left = 1440, Header = 720, Footer = 720 }
                )
            )
        ));
    }

    // ============================================================================
    // Body Content Section
    // ============================================================================
    private static void AddContentSection(WordprocessingDocument doc, Body body, string bodyImageId, MainDocumentPart mainPart, string bgDir)
    {
        // Add body background via Header - image must be added to HeaderPart
        var headerPart = mainPart.AddNewPart<HeaderPart>();
        var headerId = mainPart.GetIdOfPart(headerPart);

        // Add background image to HeaderPart
        var headerImagePart = headerPart.AddImagePart(ImagePartType.Png);
        using (var stream = new FileStream(Path.Combine(bgDir, "body_bg.png"), FileMode.Open))
            headerImagePart.FeedData(stream);
        var headerImageId = headerPart.GetIdOfPart(headerImagePart);

        // Header: background image + text
        headerPart.Header = new Header(
            // Background image
            new Paragraph(new Run(CreateFloatingBackground(headerImageId, 2, "BodyBackground"))),
            // Header text
            new Paragraph(
                new ParagraphProperties(
                    new Justification { Val = JustificationValues.Right },
                    new SpacingBetweenLines { Before = "0", After = "0" }
                ),
                new Run(
                    new RunProperties(
                        new FontSize { Val = "18" },
                        new Color { Val = Colors.Light }
                    ),
                    new Text("Project Proposal")
                ),
                new Run(
                    new RunProperties(
                        new FontSize { Val = "18" },
                        new Color { Val = Colors.Primary }
                    ),
                    new Text("  |  ") { Space = SpaceProcessingModeValues.Preserve }
                ),
                new Run(
                    new RunProperties(
                        new FontSize { Val = "18" },
                        new Color { Val = Colors.Light }
                    ),
                    new Text("[Company Name]")
                )
            )
        );

        // Create footer - page numbers
        var footerPart = mainPart.AddNewPart<FooterPart>();
        var footerId = mainPart.GetIdOfPart(footerPart);
        var footerPara = new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center }
            )
        );
        footerPara.Append(CreatePageNumberField());
        footerPara.Append(new Run(new Text(" / ") { Space = SpaceProcessingModeValues.Preserve }));
        footerPara.Append(CreateTotalPagesField());
        footerPart.Footer = new Footer(footerPara);

        // ===== Executive Summary =====
        body.Append(CreateHeading1("Executive Summary", "_Toc001"));

        // Demo footnote: add footnote reference at paragraph end
        var summaryPara = new Paragraph(
            new Run(new Text("This proposal aims to address [core problem] through [solution approach], with expected outcomes of [target benefits]. Our approach has been thoroughly validated and will deliver significant efficiency gains and cost optimization for your organization."))
        );
        body.Append(summaryPara);
        AddFootnote(doc, summaryPara, "See Appendix A for detailed requirements analysis.");

        // Add native pie chart - demo cross-reference
        var refToFig1 = new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new SpacingBetweenLines { Before = "200" }
            ),
            new Run(new Text("Below is the current market share distribution ("))
        );
        // Demo cross-reference: clicking "Figure 1" jumps to chart location
        foreach (var run in CreateCrossReference("Figure1", "Figure 1"))
            refToFig1.Append(run);
        refToFig1.Append(new Run(new Text("):")));
        body.Append(refToFig1);

        // Native Word pie chart
        AddPieChart(body, mainPart, "Figure1");

        // Chart caption with bookmark for cross-reference
        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new BookmarkStart { Id = "100", Name = "Figure1" },
            new Run(new Text("Figure 1: Market Share Distribution")),
            new BookmarkEnd { Id = "100" }
        ));

        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));

        // ===== Project Background =====
        body.Append(CreateHeading1("Project Background", "_Toc002"));
        body.Append(CreateHeading2("Industry Overview"));

        body.Append(new Paragraph(
            new Run(new Text("The current market size is approximately $X billion, with an annual growth rate of X%. Major players include [Competitor A], [Competitor B], and others. The industry is undergoing a critical phase of digital transformation."))
        ));

        // ===== Insert bar chart - demo cross-reference =====
        var refToFig2 = new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new SpacingBetweenLines { Before = "200" }
            ),
            new Run(new Text("The following chart shows quarterly business growth trends over the past two years ("))
        );
        foreach (var run in CreateCrossReference("Figure2", "Figure 2"))
            refToFig2.Append(run);
        refToFig2.Append(new Run(new Text("):")));
        body.Append(refToFig2);

        // Native Word bar chart
        AddBarChart(body, mainPart);

        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new BookmarkStart { Id = "101", Name = "Figure2" },
            new Run(new Text("Figure 2: Quarterly Business Growth Comparison")),
            new BookmarkEnd { Id = "101" }
        ));

        body.Append(CreateHeading2("Customer Pain Points"));

        // Numbered list
        body.Append(CreateNumberedItem(1, "Low Efficiency", "Current solutions have slow processing speeds and cannot meet business growth demands"));
        body.Append(CreateNumberedItem(1, "High Costs", "Operating costs continue to rise, compressing profit margins"));
        body.Append(CreateNumberedItem(1, "Poor Experience", "User satisfaction is declining, customer churn rate is increasing"));

        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));

        // ===== Proposed Solution =====
        body.Append(CreateHeading1("Proposed Solution", "_Toc003"));
        body.Append(CreateHeading2("Core Modules"));

        body.Append(new Paragraph(
            new ParagraphProperties(
                new KeepNext(),  // Keep with table
                new SpacingBetweenLines { Before = "200" }
            ),
            new Run(new Text("Our proposed solution is based on advanced technology architecture and includes the following core modules:"))
        ));

        // Table - with padding
        body.Append(CreateDataTable());

        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new Run(new Text("Table 1: Core Module Overview"))
        ));

        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));

        // ===== Project Timeline =====
        body.Append(CreateHeading1("Project Timeline", "_Toc004"));

        body.Append(CreateHeading3("Phase 1: Requirements Analysis & Design"));
        body.Append(new Paragraph(new Run(new Text("Deep dive into customer business processes, complete system architecture design and detailed design documentation."))));

        body.Append(CreateHeading3("Phase 2: Development & Testing"));
        body.Append(new Paragraph(new Run(new Text("Develop according to design documents using agile methodology, continuously delivering working versions."))));

        body.Append(CreateHeading3("Phase 3: Deployment & Delivery"));
        body.Append(new Paragraph(new Run(new Text("Complete system deployment, user training, and documentation delivery to ensure smooth go-live."))));

        // Milestone table
        body.Append(new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new SpacingBetweenLines { Before = "280" }
            ),
            new Run(new Text("Key project milestones are as follows:"))
        ));

        body.Append(CreateMilestoneTable());

        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new Run(new Text("Table 2: Project Milestones"))
        ));

        // Body section properties - with Header background
        body.Append(new Paragraph(
            new ParagraphProperties(
                new SectionProperties(
                    new SectionType { Val = SectionMarkValues.NextPage },
                    new HeaderReference { Type = HeaderFooterValues.Default, Id = headerId },
                    new FooterReference { Type = HeaderFooterValues.Default, Id = footerId },
                    new PageSize { Width = (UInt32Value)(uint)A4WidthTwips, Height = (UInt32Value)(uint)A4HeightTwips },
                    new PageMargin { Top = 1800, Right = 1440, Bottom = 1440, Left = 1440, Header = 720, Footer = 720 }
                )
            )
        ));
    }

    // ============================================================================
    // Back Cover Section - Minimalist
    // ============================================================================
    private static void AddBackcoverSection(Body body, string backcoverImageId)
    {
        // Background image
        body.Append(new Paragraph(new Run(CreateFloatingBackground(backcoverImageId, 3, "BackcoverBackground"))));

        // Large whitespace
        body.Append(new Paragraph(
            new ParagraphProperties(new SpacingBetweenLines { Before = "8000" }),
            new Run()
        ));

        // Company name
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { After = "400" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "36" },
                    new Color { Val = Colors.Dark }
                ),
                new Text("[Company Name]")
            )
        ));

        // Contact info - single line
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { After = "200" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "18" },
                    new Color { Val = Colors.Light }
                ),
                new Text("contact@company.com  \u00b7  +1 (555) 123-4567")
            )
        ));

        // Copyright
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "16" },
                    new Color { Val = Colors.Light }
                ),
                new Text("\u00a9 2024")
            )
        ));

        // Final section properties
        body.Append(new SectionProperties(
            new PageSize { Width = (UInt32Value)(uint)A4WidthTwips, Height = (UInt32Value)(uint)A4HeightTwips },
            new PageMargin { Top = 0, Right = 0, Bottom = 0, Left = 0, Header = 0, Footer = 0 }
        ));
    }

    // ============================================================================
    // Helper Methods
    // ============================================================================
    private static Paragraph CreateHeading1(string text, string bookmarkName)
    {
        var bookmarkId = bookmarkName.Replace("_Toc", "");
        return new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Heading1" }),
            new BookmarkStart { Id = bookmarkId, Name = bookmarkName },
            new Run(new Text(text)),
            new BookmarkEnd { Id = bookmarkId }
        );
    }

    private static Paragraph CreateHeading2(string text)
    {
        return new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Heading2" }),
            new Run(new Text(text))
        );
    }

    private static Paragraph CreateHeading3(string text)
    {
        return new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Heading3" }),
            new Run(new Text(text))
        );
    }

    private static Paragraph CreateNumberedItem(int numId, string title, string description)
    {
        return new Paragraph(
            new ParagraphProperties(
                new NumberingProperties(
                    new NumberingLevelReference { Val = 0 },
                    new NumberingId { Val = numId }
                )
            ),
            new Run(new RunProperties(new Bold()), new Text(title)),
            new Run(new Text(": " + description))
        );
    }

    // ============================================================================
    // Table Colors - Morandi Style
    // ============================================================================
    private static class TableColors
    {
        public const string HeaderBg = "f0f4f2";       // Light green-gray header
        public const string HeaderText = "2d3a35";     // Dark green-gray text
        public const string BorderThick = "7C9885";    // Morandi green thick line
    }

    // ============================================================================
    // Data Table - Clean Three-Line Style
    // ============================================================================
    private static Table CreateDataTable()
    {
        var table = new Table();

        table.Append(new TableProperties(
            new TableWidth { Width = "5000", Type = TableWidthUnitValues.Pct },
            new TableBorders(
                new TopBorder { Val = BorderValues.Single, Size = 12, Color = TableColors.BorderThick },
                new BottomBorder { Val = BorderValues.Single, Size = 12, Color = TableColors.BorderThick },
                new LeftBorder { Val = BorderValues.Nil },
                new RightBorder { Val = BorderValues.Nil },
                new InsideHorizontalBorder { Val = BorderValues.Nil },
                new InsideVerticalBorder { Val = BorderValues.Nil }
            ),
            new TableCellMarginDefault(
                new TopMargin { Width = "150", Type = TableWidthUnitValues.Dxa },
                new TableCellLeftMargin { Width = 200, Type = TableWidthValues.Dxa },
                new BottomMargin { Width = "150", Type = TableWidthUnitValues.Dxa },
                new TableCellRightMargin { Width = 200, Type = TableWidthValues.Dxa }
            )
        ));

        table.Append(new TableGrid(
            new GridColumn { Width = "2200" },
            new GridColumn { Width = "5800" },
            new GridColumn { Width = "2000" }
        ));

        table.Append(CreateSimpleHeaderRow(new[] { "Module Name", "Functionality", "Timeline" }));
        table.Append(CreateSimpleDataRow(new[] { "Core Engine", "Handles data processing and business logic, supports high concurrency", "4 weeks" }));
        table.Append(CreateSimpleDataRow(new[] { "User Interface", "Provides intuitive user experience with responsive design", "3 weeks" }));
        table.Append(CreateSimpleDataRow(new[] { "Analytics", "Generates visual reports, provides deep business insights", "2 weeks" }));
        table.Append(CreateSimpleDataRow(new[] { "API Gateway", "Unified interface management with rate limiting and authentication", "2 weeks" }));

        return table;
    }

    // ============================================================================
    // Milestone Table - Clean Three-Line Style
    // ============================================================================
    private static Table CreateMilestoneTable()
    {
        var table = new Table();

        table.Append(new TableProperties(
            new TableWidth { Width = "5000", Type = TableWidthUnitValues.Pct },
            new TableBorders(
                new TopBorder { Val = BorderValues.Single, Size = 12, Color = TableColors.BorderThick },
                new BottomBorder { Val = BorderValues.Single, Size = 12, Color = TableColors.BorderThick },
                new LeftBorder { Val = BorderValues.Nil },
                new RightBorder { Val = BorderValues.Nil },
                new InsideHorizontalBorder { Val = BorderValues.Nil },
                new InsideVerticalBorder { Val = BorderValues.Nil }
            ),
            new TableCellMarginDefault(
                new TopMargin { Width = "150", Type = TableWidthUnitValues.Dxa },
                new TableCellLeftMargin { Width = 200, Type = TableWidthValues.Dxa },
                new BottomMargin { Width = "150", Type = TableWidthUnitValues.Dxa },
                new TableCellRightMargin { Width = 200, Type = TableWidthValues.Dxa }
            )
        ));

        table.Append(new TableGrid(
            new GridColumn { Width = "1600" },
            new GridColumn { Width = "5400" },
            new GridColumn { Width = "3000" }
        ));

        table.Append(CreateSimpleHeaderRow(new[] { "Phase", "Deliverables", "Target Date" }));
        table.Append(CreateSimpleDataRow(new[] { "M1", "Requirements specification, system architecture design documents", "Week 2" }));
        table.Append(CreateSimpleDataRow(new[] { "M2", "Core functionality development complete, unit tests passing", "Week 6" }));
        table.Append(CreateSimpleDataRow(new[] { "M3", "Integration testing, user acceptance testing", "Week 8" }));
        table.Append(CreateSimpleDataRow(new[] { "M4", "Production deployment, operations handover", "Week 10" }));

        return table;
    }

    // ============================================================================
    // Simple Header Row - Gray background + bold + bottom line
    // ============================================================================
    private static TableRow CreateSimpleHeaderRow(string[] cells)
    {
        var row = new TableRow();
        row.Append(new TableRowProperties(
            new TableHeader(),
            new TableRowHeight { Val = 400, HeightType = HeightRuleValues.AtLeast }
        ));

        foreach (var cellText in cells)
        {
            var cell = new TableCell(
                new TableCellProperties(
                    new TableCellWidth { Width = "0", Type = TableWidthUnitValues.Auto },
                    new Shading { Val = ShadingPatternValues.Clear, Fill = TableColors.HeaderBg },
                    new TableCellVerticalAlignment { Val = TableVerticalAlignmentValues.Center },
                    new TableCellBorders(
                        new BottomBorder { Val = BorderValues.Single, Size = 6, Color = TableColors.BorderThick }
                    )
                ),
                new Paragraph(
                    new ParagraphProperties(
                        new Justification { Val = JustificationValues.Center },
                        new SpacingBetweenLines { Before = "0", After = "0" }
                    ),
                    new Run(
                        new RunProperties(
                            new Bold(),
                            new Color { Val = TableColors.HeaderText },
                            new FontSize { Val = "21" }
                        ),
                        new Text(cellText)
                    )
                )
            );
            row.Append(cell);
        }

        return row;
    }

    // ============================================================================
    // Simple Data Row
    // ============================================================================
    private static TableRow CreateSimpleDataRow(string[] cells)
    {
        var row = new TableRow();
        row.Append(new TableRowProperties(
            new TableRowHeight { Val = 380, HeightType = HeightRuleValues.AtLeast }
        ));

        for (int i = 0; i < cells.Length; i++)
        {
            var cell = new TableCell(
                new TableCellProperties(
                    new TableCellWidth { Width = "0", Type = TableWidthUnitValues.Auto },
                    new TableCellVerticalAlignment { Val = TableVerticalAlignmentValues.Center }
                ),
                new Paragraph(
                    new ParagraphProperties(
                        new Justification { Val = i == 0 ? JustificationValues.Center : JustificationValues.Left },
                        new SpacingBetweenLines { Before = "0", After = "0" }
                    ),
                    new Run(
                        new RunProperties(
                            new Color { Val = Colors.Dark },
                            new FontSize { Val = "21" }
                        ),
                        new Text(cells[i])
                    )
                )
            );
            row.Append(cell);
        }

        return row;
    }

    // ============================================================================
    // Create Pie Chart
    // ============================================================================
    private static void AddPieChart(Body body, MainDocumentPart mainPart, string bookmarkName)
    {
        // Create ChartPart
        var chartPart = mainPart.AddNewPart<ChartPart>();
        string chartId = mainPart.GetIdOfPart(chartPart);

        // Build pie chart
        chartPart.ChartSpace = CreatePieChartSpace();

        // Chart dimensions (EMU) - square ratio looks better for pie charts
        long chartWidth = 4572000;   // ~12 cm
        long chartHeight = 3429000;  // ~9 cm

        // Create inline chart Drawing
        var drawing = new Drawing(
            new DW.Inline(
                new DW.Extent { Cx = chartWidth, Cy = chartHeight },
                new DW.EffectExtent { LeftEdge = 0, TopEdge = 0, RightEdge = 0, BottomEdge = 0 },
                new DW.DocProperties { Id = 11, Name = "Chart Pie" },
                new DW.NonVisualGraphicFrameDrawingProperties(
                    new A.GraphicFrameLocks { NoChangeAspect = true }
                ),
                new A.Graphic(
                    new A.GraphicData(
                        new C.ChartReference { Id = chartId }
                    )
                    { Uri = "http://schemas.openxmlformats.org/drawingml/2006/chart" }
                )
            )
            { DistanceFromTop = 0, DistanceFromBottom = 0, DistanceFromLeft = 0, DistanceFromRight = 0 }
        );

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }),
            new Run(drawing)
        ));
    }

    private static C.ChartSpace CreatePieChartSpace()
    {
        var chartSpace = new C.ChartSpace();
        chartSpace.AddNamespaceDeclaration("c", "http://schemas.openxmlformats.org/drawingml/2006/chart");
        chartSpace.AddNamespaceDeclaration("a", "http://schemas.openxmlformats.org/drawingml/2006/main");

        var chart = new C.Chart();
        var plotArea = new C.PlotArea();

        // Pie chart
        var pieChart = new C.PieChart(
            new C.VaryColors { Val = true }
        );

        // Data series - Morandi colors
        var series = new C.PieChartSeries();
        series.Append(new C.Index { Val = 0 });
        series.Append(new C.Order { Val = 0 });
        series.Append(new C.SeriesText(new C.NumericValue("Market Share")));

        // Data point colors - Morandi palette
        string[] morandiColors = { "7C9885", "8B9DC3", "B4A992", "C9A9A6", "9CAF88" };
        string[] categories = { "Product A", "Product B", "Product C", "Product D", "Others" };
        double[] values = { 35, 25, 20, 12, 8 };

        for (uint i = 0; i < morandiColors.Length; i++)
        {
            series.Append(new C.DataPoint(
                new C.Index { Val = i },
                new C.Bubble3D { Val = false },
                new C.ChartShapeProperties(
                    new A.SolidFill(new A.RgbColorModelHex { Val = morandiColors[i] })
                )
            ));
        }

        // Category data
        var categoryData = new C.CategoryAxisData();
        var strRef = new C.StringReference();
        var strCache = new C.StringCache();
        strCache.Append(new C.PointCount { Val = (uint)categories.Length });
        for (int i = 0; i < categories.Length; i++)
        {
            strCache.Append(new C.StringPoint(new C.NumericValue(categories[i])) { Index = (uint)i });
        }
        strRef.Append(strCache);
        categoryData.Append(strRef);
        series.Append(categoryData);

        // Values data
        var valuesData = new C.Values();
        var numRef = new C.NumberReference();
        var numCache = new C.NumberingCache();
        numCache.Append(new C.FormatCode("General"));
        numCache.Append(new C.PointCount { Val = (uint)values.Length });
        for (int i = 0; i < values.Length; i++)
        {
            numCache.Append(new C.NumericPoint(new C.NumericValue(values[i].ToString())) { Index = (uint)i });
        }
        numRef.Append(numCache);
        valuesData.Append(numRef);
        series.Append(valuesData);

        pieChart.Append(series);
        plotArea.Append(pieChart);
        chart.Append(plotArea);

        // Legend
        chart.Append(new C.Legend(
            new C.LegendPosition { Val = C.LegendPositionValues.Right },
            new C.Overlay { Val = false }
        ));

        chart.Append(new C.PlotVisibleOnly { Val = true });
        chartSpace.Append(chart);

        return chartSpace;
    }

    // ============================================================================
    // Create Bar Chart
    // ============================================================================
    private static void AddBarChart(Body body, MainDocumentPart mainPart)
    {
        // Create ChartPart
        var chartPart = mainPart.AddNewPart<ChartPart>();
        string chartId = mainPart.GetIdOfPart(chartPart);

        // Build chart
        chartPart.ChartSpace = CreateBarChartSpace();

        // Chart dimensions (EMU)
        long chartWidth = 5486400;  // ~14.4 cm
        long chartHeight = 2743200; // ~7.2 cm

        // Create inline chart Drawing
        var drawing = new Drawing(
            new DW.Inline(
                new DW.Extent { Cx = chartWidth, Cy = chartHeight },
                new DW.EffectExtent { LeftEdge = 0, TopEdge = 0, RightEdge = 0, BottomEdge = 0 },
                new DW.DocProperties { Id = 10, Name = "Chart 1" },
                new DW.NonVisualGraphicFrameDrawingProperties(
                    new A.GraphicFrameLocks { NoChangeAspect = true }
                ),
                new A.Graphic(
                    new A.GraphicData(
                        new C.ChartReference { Id = chartId }
                    )
                    { Uri = "http://schemas.openxmlformats.org/drawingml/2006/chart" }
                )
            )
            { DistanceFromTop = 0, DistanceFromBottom = 0, DistanceFromLeft = 0, DistanceFromRight = 0 }
        );

        body.Append(new Paragraph(
            new ParagraphProperties(new Justification { Val = JustificationValues.Center }),
            new Run(drawing)
        ));
    }

    private static C.ChartSpace CreateBarChartSpace()
    {
        var chartSpace = new C.ChartSpace();
        chartSpace.AddNamespaceDeclaration("c", "http://schemas.openxmlformats.org/drawingml/2006/chart");
        chartSpace.AddNamespaceDeclaration("a", "http://schemas.openxmlformats.org/drawingml/2006/main");

        // Chart
        var chart = new C.Chart();

        // Plot area
        var plotArea = new C.PlotArea();

        // Bar chart
        var barChart = new C.BarChart(
            new C.BarDirection { Val = C.BarDirectionValues.Column },
            new C.BarGrouping { Val = C.BarGroupingValues.Clustered },
            new C.VaryColors { Val = false }
        );

        // Data series 1: 2023 - Morandi gray-blue
        var series1 = CreateBarChartSeries(
            0,
            "2023",
            new[] { "Q1", "Q2", "Q3", "Q4" },
            new[] { 85.0, 92.0, 88.0, 95.0 },
            Colors.Secondary  // Morandi gray-blue
        );
        barChart.Append(series1);

        // Data series 2: 2024 - Morandi sage green
        var series2 = CreateBarChartSeries(
            1,
            "2024",
            new[] { "Q1", "Q2", "Q3", "Q4" },
            new[] { 102.0, 115.0, 108.0, 125.0 },
            Colors.Primary  // Morandi sage green
        );
        barChart.Append(series2);

        // Axis IDs
        barChart.Append(new C.AxisId { Val = 1 });  // Category Axis
        barChart.Append(new C.AxisId { Val = 2 });  // Value Axis

        plotArea.Append(barChart);

        // Category axis (X-axis)
        var categoryAxis = new C.CategoryAxis(
            new C.AxisId { Val = 1 },
            new C.Scaling(new C.Orientation { Val = C.OrientationValues.MinMax }),
            new C.Delete { Val = false },
            new C.AxisPosition { Val = C.AxisPositionValues.Bottom },
            new C.TickLabelPosition { Val = C.TickLabelPositionValues.NextTo },
            new C.CrossingAxis { Val = 2 },
            new C.Crosses { Val = C.CrossesValues.AutoZero },
            new C.AutoLabeled { Val = true }
        );
        plotArea.Append(categoryAxis);

        // Value axis (Y-axis)
        var valueAxis = new C.ValueAxis(
            new C.AxisId { Val = 2 },
            new C.Scaling(new C.Orientation { Val = C.OrientationValues.MinMax }),
            new C.Delete { Val = false },
            new C.AxisPosition { Val = C.AxisPositionValues.Left },
            new C.MajorGridlines(),
            new C.NumberingFormat { FormatCode = "General", SourceLinked = true },
            new C.TickLabelPosition { Val = C.TickLabelPositionValues.NextTo },
            new C.CrossingAxis { Val = 1 },
            new C.Crosses { Val = C.CrossesValues.AutoZero }
        );
        plotArea.Append(valueAxis);

        chart.Append(plotArea);

        // Legend
        chart.Append(new C.Legend(
            new C.LegendPosition { Val = C.LegendPositionValues.Bottom },
            new C.Overlay { Val = false }
        ));

        // Plot visible area
        chart.Append(new C.PlotVisibleOnly { Val = true });

        chartSpace.Append(chart);

        return chartSpace;
    }

    private static C.BarChartSeries CreateBarChartSeries(
        uint index,
        string seriesName,
        string[] categories,
        double[] values,
        string color)
    {
        var series = new C.BarChartSeries();

        // Index
        series.Append(new C.Index { Val = index });
        series.Append(new C.Order { Val = index });

        // Series name
        series.Append(new C.SeriesText(
            new C.NumericValue(seriesName)
        ));

        // Fill color
        series.Append(new C.ChartShapeProperties(
            new A.SolidFill(new A.RgbColorModelHex { Val = color })
        ));

        // Category data
        var categoryData = new C.CategoryAxisData();
        var strRef = new C.StringReference();
        var strCache = new C.StringCache();
        strCache.Append(new C.PointCount { Val = (uint)categories.Length });
        for (int i = 0; i < categories.Length; i++)
        {
            strCache.Append(new C.StringPoint(new C.NumericValue(categories[i])) { Index = (uint)i });
        }
        strRef.Append(strCache);
        categoryData.Append(strRef);
        series.Append(categoryData);

        // Values data
        var valuesData = new C.Values();
        var numRef = new C.NumberReference();
        var numCache = new C.NumberingCache();
        numCache.Append(new C.FormatCode("General"));
        numCache.Append(new C.PointCount { Val = (uint)values.Length });
        for (int i = 0; i < values.Length; i++)
        {
            numCache.Append(new C.NumericPoint(new C.NumericValue(values[i].ToString())) { Index = (uint)i });
        }
        numRef.Append(numCache);
        valuesData.Append(numRef);
        series.Append(valuesData);

        return series;
    }

    // ============================================================================
    // Set Update Fields On Open
    // ============================================================================
    private static void SetUpdateFieldsOnOpen(MainDocumentPart mainPart)
    {
        var settingsPart = mainPart.AddNewPart<DocumentSettingsPart>();
        settingsPart.Settings = new Settings(
            new UpdateFieldsOnOpen { Val = true },
            new DisplayBackgroundShape()
        );
    }

    // ============================================================================
    // Numbering - Basic bullet/number list definition
    // ============================================================================
    private static Numbering CreateBasicNumbering()
    {
        return new Numbering(
            new AbstractNum(
                new Level(
                    new NumberingFormat { Val = NumberFormatValues.Decimal },
                    new LevelText { Val = "%1." },
                    new LevelJustification { Val = LevelJustificationValues.Left },
                    new ParagraphProperties(new Indentation { Left = "720", Hanging = "360" })
                ) { LevelIndex = 0 }
            ) { AbstractNumberId = 1 },
            new NumberingInstance(new AbstractNumId { Val = 1 }) { NumberID = 1 }
        );
    }

    // ============================================================================
    // Page Number Field - PAGE / NUMPAGES
    // ============================================================================
    private static Run CreatePageNumberField()
    {
        return new Run(
            new FieldChar { FieldCharType = FieldCharValues.Begin },
            new FieldCode(" PAGE ") { Space = SpaceProcessingModeValues.Preserve },
            new FieldChar { FieldCharType = FieldCharValues.Separate },
            new Text("1"),
            new FieldChar { FieldCharType = FieldCharValues.End }
        );
    }

    private static Run CreateTotalPagesField()
    {
        return new Run(
            new FieldChar { FieldCharType = FieldCharValues.Begin },
            new FieldCode(" NUMPAGES ") { Space = SpaceProcessingModeValues.Preserve },
            new FieldChar { FieldCharType = FieldCharValues.Separate },
            new Text("1"),
            new FieldChar { FieldCharType = FieldCharValues.End }
        );
    }

    // ============================================================================
    // Footnote - Add footnote to paragraph
    // ============================================================================
    private static void AddFootnote(WordprocessingDocument doc, Paragraph para, string noteText)
    {
        var mainPart = doc.MainDocumentPart!;

        // Ensure FootnotesPart exists with required separator notes
        if (mainPart.FootnotesPart == null)
        {
            var fnPart = mainPart.AddNewPart<FootnotesPart>();
            fnPart.Footnotes = new Footnotes(
                // Id=-1: Separator (required)
                new Footnote(
                    new Paragraph(new Run(new SeparatorMark()))
                ) { Type = FootnoteEndnoteValues.Separator, Id = -1 },
                // Id=0: ContinuationSeparator (required)
                new Footnote(
                    new Paragraph(new Run(new ContinuationSeparatorMark()))
                ) { Type = FootnoteEndnoteValues.ContinuationSeparator, Id = 0 }
            );
        }

        // Generate new footnote ID
        var footnotes = mainPart.FootnotesPart!.Footnotes!;
        int newId = (int)(footnotes.Elements<Footnote>().Max(fn => fn.Id?.Value ?? 0) + 1);

        // Add footnote content
        footnotes.Append(new Footnote(
            new Paragraph(
                new Run(
                    new RunProperties(new VerticalTextAlignment { Val = VerticalPositionValues.Superscript }),
                    new FootnoteReferenceMark()
                ),
                new Run(new Text(" " + noteText) { Space = SpaceProcessingModeValues.Preserve })
            )
        ) { Id = newId });

        // Add reference in paragraph
        para.Append(new Run(
            new RunProperties(new VerticalTextAlignment { Val = VerticalPositionValues.Superscript }),
            new FootnoteReference { Id = newId }
        ));
    }

    // ============================================================================
    // Cross-Reference - Hyperlink to bookmark
    // ============================================================================
    private static IEnumerable<Run> CreateCrossReference(string bookmarkName, string displayText)
    {
        yield return new Run(new FieldChar { FieldCharType = FieldCharValues.Begin });
        yield return new Run(new FieldCode($" REF {bookmarkName} \\h ") { Space = SpaceProcessingModeValues.Preserve });
        yield return new Run(new FieldChar { FieldCharType = FieldCharValues.Separate });
        yield return new Run(
            new RunProperties(new Color { Val = Colors.Primary }),
            new Text(displayText)
        );
        yield return new Run(new FieldChar { FieldCharType = FieldCharValues.End });
    }
}
