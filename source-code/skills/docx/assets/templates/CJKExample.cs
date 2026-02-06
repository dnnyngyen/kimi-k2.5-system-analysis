// CJKExample.cs - 中文内容正确写法示例
// 本文件演示中文场景下特殊字符的正确处理方式，特别是中文引号
//
// ⚠️ 核心问题：中文引号 "" 会被C#编译器误认为字符串分隔符，导致 CS1003 错误
// ✓ 解决方案：使用 Unicode 转义序列 \u201c \u201d
//
// 错误示例 (编译失败):
//   new Text("请点击"确定"按钮")  // CS1003: Syntax error, ',' expected
//
// 正确示例:
//   new Text("请点击\u201c确定\u201d按钮")  // 编译成功
//
// ⚠️ 不要用 @"" 逐字字符串！\u 转义在 @"" 中不生效：
//   ❌ @"她说\u201c你好\u201d"  → 输出原始 \u201c
//   ✓  "她说\u201c你好\u201d"   → 输出 "你好"
//
// 长文本用 + 拼接：
//   new Text("第一段内容，" +
//            "她说\u201c这是引用\u201d，" +
//            "第二段内容。")

using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using DW = DocumentFormat.OpenXml.Drawing.Wordprocessing;
using A = DocumentFormat.OpenXml.Drawing;
using PIC = DocumentFormat.OpenXml.Drawing.Pictures;
using C = DocumentFormat.OpenXml.Drawing.Charts;

namespace KimiDocx;

public static class CJKExample
{
    // ============================================================================
    // 水墨侘寂配色 - 灰调禅意（与Example莫兰迪风格区分）
    // ============================================================================
    private static class Colors
    {
        // 水墨主色调
        public const string Primary = "4A5568";      // 墨灰 - 标题
        public const string Secondary = "718096";    // 银灰 - 次要
        public const string Accent = "A0AEC0";       // 浅灰蓝 - 点缀

        // 文字色阶
        public const string Dark = "1A202C";         // 浓墨 - 正文
        public const string Mid = "4A5568";          // 淡墨 - 次要文字
        public const string Light = "A0AEC0";        // 轻墨 - 辅助文字

        // 背景/边框
        public const string Border = "CBD5E0";
        public const string TableHeader = "EDF2F7";  // 宣纸白
    }

    // A4尺寸常量
    private const int A4WidthTwips = 11906;
    private const int A4HeightTwips = 16838;
    private const long A4WidthEmu = 7560000L;
    private const long A4HeightEmu = 10692000L;

    // ============================================================================
    // 添加图片
    // ============================================================================
    private static string AddImage(MainDocumentPart mainPart, string imagePath)
    {
        var imagePart = mainPart.AddImagePart(ImagePartType.Png);
        using var stream = new FileStream(imagePath, FileMode.Open);
        imagePart.FeedData(stream);
        return mainPart.GetIdOfPart(imagePart);
    }

    // ============================================================================
    // 创建浮动背景图 - 置于文字下方
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
                BehindDoc = true,  // 关键：置于文字下方
                Locked = false,
                LayoutInCell = true,
                AllowOverlap = true
            }
        );
    }

    public static void Generate(string outputPath, string bgDir)
    {
        using var doc = WordprocessingDocument.Create(outputPath, WordprocessingDocumentType.Document);
        var mainPart = doc.AddMainDocumentPart();
        mainPart.Document = new Document(new Body());
        var body = mainPart.Document.Body!;

        AddStyles(mainPart);
        AddNumbering(mainPart);

        // 添加背景图关系
        var coverImageId = AddImage(mainPart, Path.Combine(bgDir, "cover_bg.png"));
        var bodyImageId = AddImage(mainPart, Path.Combine(bgDir, "body_bg.png"));
        var backcoverImageId = AddImage(mainPart, Path.Combine(bgDir, "backcover_bg.png"));

        // ========== 封面 ==========
        AddCoverSection(body, coverImageId);

        // ========== 目录 ==========
        AddTocSection(body, mainPart);

        // ========== 正文 ==========
        AddContentSection(doc, body, mainPart, bgDir);

        // ========== 封底 ==========
        AddBackcoverSection(body, backcoverImageId);

        SetUpdateFieldsOnOpen(mainPart);
        doc.Save();
        Console.WriteLine($"生成完成: {outputPath}");
    }

    // ============================================================================
    // 样式定义 - 中文字体配置
    // ============================================================================
    private static void AddStyles(MainDocumentPart mainPart)
    {
        var stylesPart = mainPart.AddNewPart<StyleDefinitionsPart>();
        stylesPart.Styles = new Styles();

        // 正文样式 - 中文正文使用宋体或微软雅黑
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "Normal" },
            new StyleParagraphProperties(
                new SpacingBetweenLines { After = "200", Line = "360", LineRule = LineSpacingRuleValues.Auto },
                new Indentation { FirstLine = "420" }  // 中文段落首行缩进2字符
            ),
            new StyleRunProperties(
                // EastAsia 字体用于中文显示
                new RunFonts { Ascii = "Calibri", HighAnsi = "Calibri", EastAsia = "Microsoft YaHei" },
                new FontSize { Val = "21" },  // 10.5pt - 中文正文标准字号
                new Color { Val = Colors.Dark }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Normal", Default = true });

        // 标题1 - 中文标题使用黑体或微软雅黑加粗
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "heading 1" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepNext(),
                new KeepLines(),
                new SpacingBetweenLines { Before = "600", After = "300", Line = "240", LineRule = LineSpacingRuleValues.Auto },
                new Indentation { FirstLine = "0" },  // 标题不缩进
                new OutlineLevel { Val = 0 }
            ),
            new StyleRunProperties(
                new RunFonts { EastAsia = "SimHei" },  // 黑体用于标题
                new Bold(),
                new Color { Val = Colors.Primary },
                new FontSize { Val = "32" }  // 16pt
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Heading1" });

        // 标题2
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "heading 2" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepNext(),
                new KeepLines(),
                new SpacingBetweenLines { Before = "400", After = "200" },
                new Indentation { FirstLine = "0" },
                new OutlineLevel { Val = 1 }
            ),
            new StyleRunProperties(
                new RunFonts { EastAsia = "SimHei" },
                new Bold(),
                new Color { Val = Colors.Dark },
                new FontSize { Val = "28" }  // 14pt
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Heading2" });

        // 标题3
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "heading 3" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepNext(),
                new KeepLines(),
                new SpacingBetweenLines { Before = "280", After = "120" },
                new Indentation { FirstLine = "0" },
                new OutlineLevel { Val = 2 }
            ),
            new StyleRunProperties(
                new Bold(),
                new Color { Val = Colors.Mid },
                new FontSize { Val = "24" }  // 12pt
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Heading3" });

        // 图表标题
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "Caption" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new KeepLines(),
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { Before = "60", After = "400" },
                new Indentation { FirstLine = "0" }
            ),
            new StyleRunProperties(
                new Color { Val = Colors.Mid },
                new FontSize { Val = "20" }  // 10pt
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "Caption" });

        // 目录样式
        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "toc 1" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new Tabs(new TabStop { Val = TabStopValues.Right, Leader = TabStopLeaderCharValues.Dot, Position = 9350 }),
                new SpacingBetweenLines { Before = "200", After = "60" },
                new Indentation { FirstLine = "0" }
            ),
            new StyleRunProperties(
                new Bold(),
                new Color { Val = Colors.Dark }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "TOC1" });

        stylesPart.Styles.Append(new Style(
            new StyleName { Val = "toc 2" },
            new BasedOn { Val = "Normal" },
            new StyleParagraphProperties(
                new Tabs(new TabStop { Val = TabStopValues.Right, Leader = TabStopLeaderCharValues.Dot, Position = 9350 }),
                new SpacingBetweenLines { Before = "60", After = "60" },
                new Indentation { Left = "420", FirstLine = "0" }
            ),
            new StyleRunProperties(
                new Color { Val = Colors.Mid }
            )
        )
        { Type = StyleValues.Paragraph, StyleId = "TOC2" });
    }

    // ============================================================================
    // 编号定义
    // ============================================================================
    private static void AddNumbering(MainDocumentPart mainPart)
    {
        var numberingPart = mainPart.AddNewPart<NumberingDefinitionsPart>();
        numberingPart.Numbering = new Numbering(
            new AbstractNum(
                new Level(
                    new StartNumberingValue { Val = 1 },  // 从1开始，不是0
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
    // 封面 - 中文项目封面
    // ============================================================================
    private static void AddCoverSection(Body body, string coverImageId)
    {
        // 背景图
        body.Append(new Paragraph(new Run(CreateFloatingBackground(coverImageId, 1, "CoverBackground"))));

        // 大间距
        body.Append(new Paragraph(
            new ParagraphProperties(new SpacingBetweenLines { Before = "6000" }),
            new Run()
        ));

        // 主标题
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { After = "400" }
            ),
            new Run(
                new RunProperties(
                    new RunFonts { EastAsia = "SimHei" },
                    new FontSize { Val = "72" },  // 36pt
                    new Color { Val = Colors.Primary }
                ),
                new Text("项目方案书")
            )
        ));

        // 副标题 - 演示引号的正确使用
        // ❌ Wrong: new Text("\"智慧城市\"建设项目")  // 这里如果写中文引号会报错
        // ✓ Correct: 使用 Unicode 转义或常量
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { After = "3000" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "28" },
                    new Color { Val = Colors.Secondary }
                ),
                // 中文引号使用 \u201c \u201d
                new Text("\u201c智慧城市\u201d建设项目")
            )
        ));

        // 公司名称
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { After = "120" }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "24" },
                    new Color { Val = Colors.Light }
                ),
                new Text("某某科技有限公司")
            )
        ));

        // 日期
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "21" },
                    new Color { Val = Colors.Light }
                ),
                new Text("2024年12月")
            )
        ));

        // 封面分节符
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
    // 目录
    // ============================================================================
    private static void AddTocSection(Body body, MainDocumentPart mainPart)
    {
        // 目录标题
        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Heading1" }),
            new BookmarkStart { Id = "0", Name = "_Toc000" },
            new Run(new Text("目录")),
            new BookmarkEnd { Id = "0" }
        ));

        // 目录刷新提示 - 这是最常出错的地方！
        // ❌ Wrong: new Text("右键点击目录选择"更新域"刷新页码")  // CS1003 编译错误！
        // ✓ Correct: 使用 \u201c 和 \u201d
        body.Append(new Paragraph(
            new ParagraphProperties(new SpacingBetweenLines { After = "300" }),
            new Run(
                new RunProperties(
                    new Color { Val = Colors.Light },
                    new FontSize { Val = "18" }
                ),
                // 正确写法示例1：直接使用 Unicode 转义
                new Text("（提示：首次打开请右键点击目录，选择\u201c更新域\u201d刷新页码）")
            )
        ));

        // 目录域代码
        body.Append(new Paragraph(
            new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }),
            new Run(new FieldCode(" TOC \\o \"1-3\" \\h \\z \\u ") { Space = SpaceProcessingModeValues.Preserve }),
            new Run(new FieldChar { FieldCharType = FieldCharValues.Separate })
        ));

        // 目录占位条目
        string[,] tocEntries = {
            { "项目概述", "1", "3" },
            { "需求分析", "1", "4" },
            { "功能需求", "2", "4" },
            { "非功能需求", "2", "5" },
            { "技术方案", "1", "6" },
            { "项目计划", "1", "8" }
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

        // 目录域结束
        body.Append(new Paragraph(
            new Run(new FieldChar { FieldCharType = FieldCharValues.End })
        ));

        // 目录分节符
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
    // 正文内容 - 演示各种中文引号场景
    // ============================================================================
    private static void AddContentSection(WordprocessingDocument doc, Body body, MainDocumentPart mainPart, string bgDir)
    {
        // 创建页眉（含正文背景图）
        var headerPart = mainPart.AddNewPart<HeaderPart>();
        var headerId = mainPart.GetIdOfPart(headerPart);

        // 将背景图添加到 HeaderPart
        var headerImagePart = headerPart.AddImagePart(ImagePartType.Png);
        using (var stream = new FileStream(Path.Combine(bgDir, "body_bg.png"), FileMode.Open))
            headerImagePart.FeedData(stream);
        var headerImageId = headerPart.GetIdOfPart(headerImagePart);

        headerPart.Header = new Header(
            // 背景图
            new Paragraph(new Run(CreateFloatingBackground(headerImageId, 2, "BodyBackground"))),
            // 页眉文字
            new Paragraph(
                new ParagraphProperties(
                    new Justification { Val = JustificationValues.Right }
                ),
                new Run(
                    new RunProperties(
                        new FontSize { Val = "18" },
                        new Color { Val = Colors.Light }
                    ),
                    new Text("项目方案书")
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
                    new Text("某某科技有限公司")
                )
            )
        );

        // 创建页脚
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

        // ===== 第一章：项目概述 =====
        body.Append(CreateHeading1("项目概述", "_Toc001"));

        // 项目背景 - 长段落示例，展示多引号长文本的正确拼接方式
        // 注意：不使用 @"" 逐字字符串，用 + 拼接，引号用 \u201c \u201d
        var backgroundPara = new Paragraph(
            new Run(new Text(
                "随着新型城镇化进程加速推进，智慧城市建设已成为国家战略重点。" +
                "《\u201c十四五\u201d国家信息化规划》明确指出：" +
                "\u201c要以数字化转型整体驱动生产方式、生活方式和治理方式变革，" +
                "全面建设数字中国\u201d。" +
                "住建部在《关于全面推进城市信息模型基础平台建设的指导意见》中强调，" +
                "要\u201c推动城市规划建设管理多场景应用，" +
                "提升城市科学化、精细化、智能化治理水平\u201d。" +
                "本项目正是在这一背景下应运而生，" +
                "旨在构建\u201c感知、分析、服务、指挥、监察\u201d五位一体的智慧城市综合管理平台。"
            ))
        );
        body.Append(backgroundPara);
        AddFootnote(doc, backgroundPara, "引自《\u201c十四五\u201d国家信息化规划》及住建部相关文件。");

        // 书名号示例 - 《》不需要转义，可以直接使用
        body.Append(new Paragraph(
            new Run(new Text("详细内容请参阅《用户需求规格说明书》及《系统设计文档》。"))
            // ✓ 书名号《》可以直接使用，不会导致编译错误
        ));

        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));

        // ===== 第二章：需求分析 =====
        body.Append(CreateHeading1("需求分析", "_Toc002"));
        body.Append(CreateHeading2("功能需求"));

        // 强调内容示例 - 引号用 \u201c \u201d
        body.Append(new Paragraph(
            new Run(new Text("系统应在用户点击\u201c确定\u201d按钮后，在3秒内完成数据保存操作。"))
        ));

        // 编号列表
        body.Append(CreateNumberedItem(1, "用户管理", "支持\u201c增删改查\u201d等基本操作"));
        body.Append(CreateNumberedItem(1, "权限控制", "实现\u201c角色权限\u201d精细化管理"));
        body.Append(CreateNumberedItem(1, "数据分析", "提供\u201c可视化报表\u201d功能"));

        body.Append(CreateHeading2("非功能需求"));

        // 表格 - 中文表头
        body.Append(new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new SpacingBetweenLines { Before = "200" }
            ),
            new Run(new Text("系统非功能需求如下表所示："))
        ));

        body.Append(CreateRequirementTable());

        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new Run(new Text("表1：非功能需求列表"))
        ));

        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));

        // ===== 第三章：技术方案 =====
        body.Append(CreateHeading1("技术方案", "_Toc003"));

        // 技术术语中的引号
        body.Append(new Paragraph(
            new Run(new Text("本项目采用\u201c微服务\u201d架构，基于\u201c容器化\u201d部署方案。系统采用\u201c前后端分离\u201d模式开发。"))
        ));

        // 添加饼图
        var chartRef = new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new SpacingBetweenLines { Before = "200" }
            ),
            new Run(new Text("技术栈占比分布如下（"))
        );
        foreach (var run in CreateCrossReference("Figure1", "图1"))
            chartRef.Append(run);
        chartRef.Append(new Run(new Text("）：")));
        body.Append(chartRef);

        AddPieChart(body, mainPart);

        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new BookmarkStart { Id = "100", Name = "Figure1" },
            new Run(new Text("图1：技术栈占比分布")),
            new BookmarkEnd { Id = "100" }
        ));

        body.Append(new Paragraph(new Run(new Break { Type = BreakValues.Page })));

        // ===== 第四章：项目计划 =====
        body.Append(CreateHeading1("项目计划", "_Toc004"));

        body.Append(CreateHeading3("第一阶段：需求调研"));
        body.Append(new Paragraph(
            new Run(new Text("深入调研用户需求，完成\u201c需求规格说明书\u201d编写。"))
        ));

        body.Append(CreateHeading3("第二阶段：系统设计"));
        body.Append(new Paragraph(
            new Run(new Text("完成系统架构设计，输出\u201c概要设计\u201d和\u201c详细设计\u201d文档。"))
        ));

        body.Append(CreateHeading3("第三阶段：开发测试"));
        body.Append(new Paragraph(
            new Run(new Text("按照\u201c敏捷开发\u201d模式迭代交付。"))
        ));

        // 里程碑表格
        body.Append(new Paragraph(
            new ParagraphProperties(
                new KeepNext(),
                new SpacingBetweenLines { Before = "280" }
            ),
            new Run(new Text("项目关键里程碑如下："))
        ));

        body.Append(CreateMilestoneTable());

        body.Append(new Paragraph(
            new ParagraphProperties(new ParagraphStyleId { Val = "Caption" }),
            new Run(new Text("表2：项目里程碑"))
        ));

        // 正文分节符
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
    // 封底
    // ============================================================================
    private static void AddBackcoverSection(Body body, string backcoverImageId)
    {
        // 背景图
        body.Append(new Paragraph(new Run(CreateFloatingBackground(backcoverImageId, 3, "BackcoverBackground"))));

        // 大间距
        body.Append(new Paragraph(
            new ParagraphProperties(new SpacingBetweenLines { Before = "8000" }),
            new Run()
        ));

        // 公司名称
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center },
                new SpacingBetweenLines { After = "400" }
            ),
            new Run(
                new RunProperties(
                    new RunFonts { EastAsia = "SimHei" },
                    new FontSize { Val = "36" },
                    new Color { Val = Colors.Dark }
                ),
                new Text("某某科技有限公司")
            )
        ));

        // 联系方式
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
                new Text("contact@example.com  \u00b7  +86 123-4567-8900")
            )
        ));

        // 版权
        body.Append(new Paragraph(
            new ParagraphProperties(
                new Justification { Val = JustificationValues.Center }
            ),
            new Run(
                new RunProperties(
                    new FontSize { Val = "16" },
                    new Color { Val = Colors.Light }
                ),
                new Text("\u00a9 2024 版权所有")
            )
        ));

        // 最终分节符
        body.Append(new SectionProperties(
            new PageSize { Width = (UInt32Value)(uint)A4WidthTwips, Height = (UInt32Value)(uint)A4HeightTwips },
            new PageMargin { Top = 0, Right = 0, Bottom = 0, Left = 0, Header = 0, Footer = 0 }
        ));
    }

    // ============================================================================
    // 辅助方法
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
            new Run(new Text("：" + description))  // 使用中文冒号
        );
    }

    // ============================================================================
    // 需求表格
    // ============================================================================
    private static Table CreateRequirementTable()
    {
        var table = new Table();

        table.Append(new TableProperties(
            new TableWidth { Width = "5000", Type = TableWidthUnitValues.Pct },
            new TableBorders(
                new TopBorder { Val = BorderValues.Single, Size = 12, Color = Colors.Primary },
                new BottomBorder { Val = BorderValues.Single, Size = 12, Color = Colors.Primary },
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
            new GridColumn { Width = "2000" },
            new GridColumn { Width = "4000" },
            new GridColumn { Width = "2000" }
        ));

        var widths = new[] { "2000", "4000", "2000" };

        // 中文表头
        table.Append(CreateHeaderRow(new[] { "需求类型", "需求描述", "优先级" }, widths));
        table.Append(CreateDataRow(new[] { "性能", "系统响应时间小于3秒", "高" }, widths));
        table.Append(CreateDataRow(new[] { "可用性", "系统可用性达到99.9%", "高" }, widths));
        table.Append(CreateDataRow(new[] { "安全性", "支持\u201c等保三级\u201d要求", "高" }, widths));
        table.Append(CreateDataRow(new[] { "可维护性", "提供完善的日志和监控", "中" }, widths));

        return table;
    }

    // ============================================================================
    // 里程碑表格
    // ============================================================================
    private static Table CreateMilestoneTable()
    {
        var table = new Table();

        table.Append(new TableProperties(
            new TableWidth { Width = "5000", Type = TableWidthUnitValues.Pct },
            new TableBorders(
                new TopBorder { Val = BorderValues.Single, Size = 12, Color = Colors.Primary },
                new BottomBorder { Val = BorderValues.Single, Size = 12, Color = Colors.Primary },
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

        var widths = new[] { "1600", "5400", "3000" };

        table.Append(CreateHeaderRow(new[] { "阶段", "交付物", "计划时间" }, widths));
        table.Append(CreateDataRow(new[] { "M1", "《需求规格说明书》", "第2周" }, widths));
        table.Append(CreateDataRow(new[] { "M2", "《系统设计文档》", "第4周" }, widths));
        table.Append(CreateDataRow(new[] { "M3", "核心功能开发完成", "第8周" }, widths));
        table.Append(CreateDataRow(new[] { "M4", "系统上线运行", "第12周" }, widths));

        return table;
    }

    private static TableRow CreateHeaderRow(string[] cells, string[] widths)
    {
        var row = new TableRow();
        row.Append(new TableRowProperties(
            new TableHeader(),
            new TableRowHeight { Val = 400, HeightType = HeightRuleValues.AtLeast }
        ));

        for (int i = 0; i < cells.Length; i++)
        {
            var cell = new TableCell(
                new TableCellProperties(
                    new TableCellWidth { Width = widths[i], Type = TableWidthUnitValues.Dxa },
                    new Shading { Val = ShadingPatternValues.Clear, Fill = Colors.TableHeader },
                    new TableCellVerticalAlignment { Val = TableVerticalAlignmentValues.Center },
                    new TableCellBorders(
                        new BottomBorder { Val = BorderValues.Single, Size = 6, Color = Colors.Primary }
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

    private static TableRow CreateDataRow(string[] cells, string[] widths)
    {
        var row = new TableRow();
        row.Append(new TableRowProperties(
            new TableRowHeight { Val = 380, HeightType = HeightRuleValues.AtLeast }
        ));

        for (int i = 0; i < cells.Length; i++)
        {
            var cell = new TableCell(
                new TableCellProperties(
                    new TableCellWidth { Width = widths[i], Type = TableWidthUnitValues.Dxa },
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
    // 饼图 - 中文标签
    // ============================================================================
    private static void AddPieChart(Body body, MainDocumentPart mainPart)
    {
        var chartPart = mainPart.AddNewPart<ChartPart>();
        string chartId = mainPart.GetIdOfPart(chartPart);

        chartPart.ChartSpace = CreatePieChartSpace();

        long chartWidth = 4572000;
        long chartHeight = 3429000;

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

        var pieChart = new C.PieChart(
            new C.VaryColors { Val = true }
        );

        var series = new C.PieChartSeries();
        series.Append(new C.Index { Val = 0 });
        series.Append(new C.Order { Val = 0 });
        series.Append(new C.SeriesText(new C.NumericValue("技术栈")));

        // 低饱和商务色 - 柔和但有区分度
        string[] colors = { "4A6FA5", "6B9080", "A67F78", "8E7B9A", "9CA3AF" };
        // 灰蓝 | 青灰 | 暖棕 | 烟紫 | 银灰
        // 中文标签 - 直接使用即可，不需要转义
        string[] categories = { "后端开发", "前端开发", "数据库", "运维部署", "其他" };
        double[] values = { 40, 25, 15, 12, 8 };

        for (uint i = 0; i < colors.Length; i++)
        {
            series.Append(new C.DataPoint(
                new C.Index { Val = i },
                new C.Bubble3D { Val = false },
                new C.ChartShapeProperties(
                    new A.SolidFill(new A.RgbColorModelHex { Val = colors[i] })
                )
            ));
        }

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

        chart.Append(new C.Legend(
            new C.LegendPosition { Val = C.LegendPositionValues.Right },
            new C.Overlay { Val = false }
        ));

        chart.Append(new C.PlotVisibleOnly { Val = true });
        chartSpace.Append(chart);

        return chartSpace;
    }

    // ============================================================================
    // 页码域
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
    // 交叉引用
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

    // ============================================================================
    // 脚注
    // ============================================================================
    private static void AddFootnote(WordprocessingDocument doc, Paragraph para, string noteText)
    {
        var mainPart = doc.MainDocumentPart!;

        if (mainPart.FootnotesPart == null)
        {
            var fnPart = mainPart.AddNewPart<FootnotesPart>();
            fnPart.Footnotes = new Footnotes(
                new Footnote(
                    new Paragraph(new Run(new SeparatorMark()))
                ) { Type = FootnoteEndnoteValues.Separator, Id = -1 },
                new Footnote(
                    new Paragraph(new Run(new ContinuationSeparatorMark()))
                ) { Type = FootnoteEndnoteValues.ContinuationSeparator, Id = 0 }
            );
        }

        var footnotes = mainPart.FootnotesPart!.Footnotes!;
        int newId = (int)(footnotes.Elements<Footnote>().Max(fn => fn.Id?.Value ?? 0) + 1);

        footnotes.Append(new Footnote(
            new Paragraph(
                new Run(
                    new RunProperties(new VerticalTextAlignment { Val = VerticalPositionValues.Superscript }),
                    new FootnoteReferenceMark()
                ),
                new Run(new Text(" " + noteText) { Space = SpaceProcessingModeValues.Preserve })
            )
        ) { Id = newId });

        para.Append(new Run(
            new RunProperties(new VerticalTextAlignment { Val = VerticalPositionValues.Superscript }),
            new FootnoteReference { Id = newId }
        ));
    }

    // ============================================================================
    // 设置打开时更新域
    // ============================================================================
    private static void SetUpdateFieldsOnOpen(MainDocumentPart mainPart)
    {
        var settingsPart = mainPart.AddNewPart<DocumentSettingsPart>();
        settingsPart.Settings = new Settings(
            new UpdateFieldsOnOpen { Val = true },
            new DisplayBackgroundShape()
        );
    }
}
