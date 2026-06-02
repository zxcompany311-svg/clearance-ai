"""
Clearance AI System - Pentagram Dark-Tech Design
Designed with $cc-design framework (v2.1)
Style: Pentagram Dark-Tech
Theme: Deep dark slate (#060913), neon aurora cyan (#00F2FE), royal violet (#7C3AED)
"""

import streamlit as st
import os
import json
import io
import base64
import time
import threading
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


# ---------------------------------------------------------
# Page Configurations & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="尼日利亚本土仓 AI 跨境清仓聚合系统",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force sidebar collapsed on startup (reset local storage and click collapse button if expanded)
if "sidebar_collapsed_forced" not in st.session_state:
    st.session_state.sidebar_collapsed_forced = True
    st.html(
        """
        <script>
            (function() {
                try {
                    // 1. Force the local storage values to be collapsed for subsequent visits
                    localStorage.setItem("stSidebarCollapsed", "true");
                    const keys = Object.keys(localStorage);
                    keys.forEach(key => {
                        if (key.includes("collapsed") || key.includes("sidebar") || key.includes("Sidebar")) {
                            localStorage.setItem(key, "true");
                        }
                    });

                    // 2. Poll until we find the collapse button and click it to fold it immediately
                    let attempts = 0;
                    const interval = setInterval(() => {
                        attempts++;
                        var collapseBtn = document.querySelector('[data-testid="stSidebarCollapseButton"]')
                                       || document.querySelector('button[aria-label="Collapse sidebar"]')
                                       || document.querySelector('button[aria-label="Close sidebar"]')
                                       || document.querySelector('button[kind="headerNoPadding"]');
                        
                        if (collapseBtn) {
                            collapseBtn.click();
                            clearInterval(interval);
                        } else if (attempts > 100) { // Stop polling after 10 seconds
                            clearInterval(interval);
                        }
                    }, 100);
                } catch (e) {
                    console.error("Error forcing sidebar collapsed:", e);
                }
            })();
        </script>
        """,
        unsafe_allow_javascript=True
    )

# Optional import of rembg
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

# ---------------------------------------------------------
# Multi-Language Translation Dictionary (i18n)
# ---------------------------------------------------------
UI_LANG = {
    "简体中文": {
        "title": "尼日利亚本土仓 AI 跨境清仓聚合系统",
        "subtitle": "为尼日利亚本土仓零售/批发清仓打造的一站式AI提效控制台。涵盖西非爆款文案生成、仓储原图“一键洗白”去噪加水印、WhatsApp 快捷谈判、国内爆款视频本土化重构以及 Meta/TikTok 社媒辅助投流。",
        "sidebar_title": "系统全局配置中心",
        "sidebar_info": "配置的全局变量将自动注入到文案生成、去噪水印、SOP 话术库以及投流建议中。",
        "sidebar_api_key": "OpenAI API Key",
        "sidebar_api_key_help": "在此处输入 API Key 以激活 GPT 服务。如果为空，系统将自动降级到「AI 模拟调试模式 (Mock Mode)」生成演示文本。",
        "sidebar_base_url": "OpenAI API Base URL",
        "sidebar_model": "LLM 驱动模型",
        "sidebar_contact_title": "本地仓联络与收款配置",
        "sidebar_phone": "WhatsApp 客服电话 (加水印 & 话术填充)",
        "sidebar_address": "拉各斯自提仓库地址 (Lagos Pickup Warehouse Address)",
        "sidebar_account_name": "收款账户名 (Bank Account Name)",
        "sidebar_account_num": "收款账号与银行 (Account Number & Bank)",
        
        "tab_copy": "📢 本土营销文案 (Text-to-Copy)",
        "tab_image": "🖼️ 图像去噪与水印 (Image-to-Product)",
        "tab_sop": "💬 WhatsApp 客服话术 (SOP Hub)",
        "tab_video": "🎬 爆款视频本土化 (Video-to-Local-Script)",
        "tab_ads": "📈 社媒投流辅助 (Ads Pilot)",
        "tab_training": "📚 培训教材与交付中心 (SOP Manual)",
        
        # Tab 1
        "t1_header": "西非本土化营销文案生成器",
        "t1_desc": "本模块接入 AI 大语言模型，可根据商品品类和关键卖点，一键生成 3 套针对尼日利亚消费群体的爆款纯英文引流文案。",
        "t1_input_header": "输入清仓商品信息",
        "t1_cat": "商品所属品类",
        "t1_name": "商品名称与规格 (品名需清晰)",
        "t1_price": "单件清仓底价 (NGN)",
        "t1_moq": "起批数量 (MOQ)",
        "t1_points": "勾选核心卖点 (可多选)",
        "t1_extra": "其他自定义卖点/通知 (如: 仅剩最终200个)",
        "t1_pidgin": "开启西非特色英语 / 皮钦语 (Pidgin English) 润色优化",
        "t1_pidgin_help": "开启后文案将穿插 'Aje', 'Na double quality', 'No story' 等尼日利亚黑人采购黑话，倍增转化率。",
        "t1_btn": "生成西非爆款清仓文案",
        "t1_out_header": "AI 本土化文案输出 (纯英文)",
        "t1_info": "请在左侧填写商品属性，然后点击「生成西非爆款清仓文案」按钮。",
        "t1_mock_title": "Meta (Facebook/IG) 广告端投流视觉仿真预览",
        "t1_mock_desc": "以下卡片是由 Vanilla CSS 渲染的仿真社媒广告卡，用于呈现文案配合上传白底商品图时的实际观感：",
        "manage_expander": "🛠️ 品类与卖点库管理",
        "add_cat": "新增品类",
        "del_cat": "选择要删除的品类",
        "add_pt": "新增核心卖点",
        "del_pt": "选择要删除的卖点",
        "add_btn": "添加",
        "del_btn": "删除",
        "dup_warn": "该项目已存在！",
        "empty_warn": "内容不能为空！",
        "success_add_cat": "添加并翻译品类成功：",
        "success_del_cat": "删除品类成功：",
        "success_add_pt": "添加并翻译卖点成功：",
        "success_del_pt": "删除卖点成功：",
        
        # Tab 2
        "t2_header": "仓储图像“一键洗白”与去噪水印模块",
        "t2_desc": "将尼日利亚仓库现场手机实拍的阴暗、杂乱图，一键去除背景，替换为高亮纯白底商品图，并自定义加盖客服防伪防盗水印。",
        "t2_input_header": "上传并自定义水印属性",
        "t2_file_label": "选择需要处理的图片 (支持 JPG, JPEG, PNG)",
        "t2_wm_header": "高级水印定制选项",
        "t2_wm_phone": "水印客服电话",
        "t2_wm_apply": "添加防伪防盗水印",
        "t2_wm_qr": "加盖WhatsApp二维码水印",
        "t2_bg_method_label": "去背景抠图算法与模型",
        "t2_wm_pos": "水印放置位置",
        "t2_wm_color": "水印边框/高亮色系",
        "t2_wm_scale": "水印字体大小占高比 (%)",
        "t2_btn": "开始净化一键洗白",
        "t2_out_header": "处理结果对比预览",
        "t2_orig": "原始上传原图",
        "t2_proc": "净化白底水印商品图",
        "t2_download": "下载洗白商品图 (JPG)",
        "t2_regenerate": "🔄 重新生成",
        "t2_info": "请先上传本地仓商品原图，然后点击「开始净化一键洗白」按钮。",
        "t2_warn": "尚未开始处理。请在左侧设定水印，然后点击「开始净化一键洗白」按钮。",
        
        # Tab 3
        "t3_header": "WhatsApp 快捷谈判与催单话术库 (Lagos Customer Service SOP Hub)",
        "t3_desc": "本话术库结合尼日利亚本地客服高频场景设计，自动关联配置的电话、仓库地址、收款账户等信息。复制即可发送。",
        "t3_setting_header": "当前聊天商品实时设定",
        "t3_active_prod": "当前被咨询商品 (Current Product)",
        "t3_active_price": "协商清仓单价 (NGN)",
        "t3_active_moq": "起批门槛 (MOQ)",
        "t3_subtab_price": "询价与价格回复 (Price Ask)",
        "t3_subtab_addr": "仓库自提指引 (Warehouse Address)",
        "t3_subtab_moq": "起批量说明 (MOQ Rules)",
        "t3_subtab_pay": "付款安全与防诈对账 (Payment & Anti-Fraud)",
        "t3_subtab_urg": "紧急催单与定金锁定 (Follow-ups & Deposit)",
        "t3_mock_label": "客服收发信真实模拟：",
        
        # Tab 4
        "t4_header": "国内爆款视频文案本土化重构引擎",
        "t4_desc": "将国内抖音、快手等平台的爆款视频文案（承重测试、源头工厂、清仓叫卖等），一键解构重构为西非黑人实拍剧本，并匹配拍摄分镜。",
        "t4_input_header": "输入国内视频文案信息",
        "t4_link_label": "国内爆款视频名称/链接 (选填，供 API 做预留解析)",
        "t4_script_label": "粘贴国内爆款中文配音/文案 (必填)",
        "t4_btn": "运行 AI 重构本土短视频脚本",
        "t4_out_header": "重构后的英文分镜拍摄脚本",
        "t4_info": "请在左侧输入需要拆解的中文原版文案，点击按钮开始重构。",
        
        # Tab 5
        "t5_header": "AI 协同社媒投流辅助控制台 (Meta/TikTok Campaign Pilot)",
        "t5_desc": "配合 Meta (Facebook/Instagram) 与 TikTok 广告后台投放，AI 自动配置 A/B 测试受众、标题文案，并提供转化率调优指南。",
        "t5_input_header": "投流属性自定义",
        "t5_channel_label": "拟投放社媒渠道",
        "t5_budget_label": "每日测试预算 (USD)",
        "t5_btn": "生成广告投流规划案",
        "t5_out_header": "投流规划方案输出",
        "t5_info": "点击左侧「生成广告投流规划案」按钮，AI 将为您输出精准定向与文案矩阵。",
        
        # Tab 6
        "t6_header": "培训教材与 SOP 交付中心 (Nigeria Warehouse Clearance SOP Manual)",
        "t6_desc": "面向国内出海团队、本地客服经理及仓库主管的标准化运营操作电子书。结合尼日利亚特有国情编制。",
        "t6_info": "本手册属于清仓核心商业模式 SOP，旨在规范海外运营操作流程，降低拒签率和网络支付诈骗风险。",
        "t6_exp1": "第一阶段：西非公域精准引流 (TikTok & Meta 投流实操)",
        "t6_exp2": "第二阶段：拉各斯本地私域社群沉淀与裂变",
        "t6_exp3": "第三阶段：货到付款 (COD) 与自提仓运营防骗指南",
        "t6_exp4": "第四阶段：本地化客服高转化接待规范"
    },
    "English": {
        "title": "Cross-Border E-commerce AI Clearance Aggregator",
        "subtitle": "One-stop AI efficiency console for retail/wholesale clearance in local Nigerian warehouses. Covers copy generation, image noise removal/watermarking, WhatsApp SOPs, video script reconstruction, and social media ad targeting pilot.",
        "sidebar_title": "System Settings",
        "sidebar_info": "Configurations will automatically update marketing text, image watermarks, SOP templates, and ad campaigns.",
        "sidebar_api_key": "OpenAI API Key",
        "sidebar_api_key_help": "Enter API Key to activate GPT service. If blank, the system runs in Mock Mode showing simulated clear-cut results.",
        "sidebar_base_url": "OpenAI API Base URL",
        "sidebar_model": "LLM Engine Model",
        "sidebar_contact_title": "Contact & Bank Settings",
        "sidebar_phone": "WhatsApp Customer Phone (Watermark & SOPs)",
        "sidebar_address": "Lagos Pickup Warehouse Address",
        "sidebar_account_name": "Bank Account Name",
        "sidebar_account_num": "Account Number & Bank",
        
        "tab_copy": "📢 Copywriter (Text-to-Copy)",
        "tab_image": "🖼️ Image Clean (Image-to-Product)",
        "tab_sop": "💬 WhatsApp SOP Hub",
        "tab_video": "🎬 Video Rebuilder",
        "tab_ads": "📈 Ads Campaign Pilot",
        "tab_training": "📚 Training SOP Manual",
        
        # Tab 1
        "t1_header": "West African Copy Generator",
        "t1_desc": "Generates 3 sets of high-energy, high-converting clearance copies tailored for Nigerian wholesale or retail customers using LLMs.",
        "t1_input_header": "Input Clearance Product Details",
        "t1_cat": "Product Category",
        "t1_name": "Product Name & Specifications",
        "t1_price": "Clearance Price (NGN)",
        "t1_moq": "Minimum Order Qty (MOQ)",
        "t1_points": "Select Key Selling Points",
        "t1_extra": "Additional Comments / Scarcity notice",
        "t1_pidgin": "Enable West African Pidgin / Slang enhancement",
        "t1_pidgin_help": "Spices up copy with Nigerian buzzwords like 'Aje', 'Na double quality', 'No story' to boost local customer interest.",
        "t1_btn": "Generate West African Clearance Copies",
        "t1_out_header": "AI Localized Copies Output",
        "t1_info": "Please fill out product details on the left, then click 'Generate West African Clearance Copies'.",
        "t1_mock_title": "Meta (Facebook/IG) Ad Visual Mockup Simulator",
        "t1_mock_desc": "Simulated card rendered via Vanilla CSS showing how the ad copies look when integrated with your cleared product image:",
        "manage_expander": "🛠️ Manage Categories & Selling Points",
        "add_cat": "Add New Category",
        "del_cat": "Select Category to Delete",
        "add_pt": "Add New Selling Point",
        "del_pt": "Select Selling Point to Delete",
        "add_btn": "Add",
        "del_btn": "Delete",
        "dup_warn": "Item already exists!",
        "empty_warn": "Content cannot be empty!",
        "success_add_cat": "Category added & translated successfully: ",
        "success_del_cat": "Category deleted successfully: ",
        "success_add_pt": "Selling point added & translated successfully: ",
        "success_del_pt": "Selling point deleted successfully: ",
        
        # Tab 2
        "t2_header": "Warehouse Image 'Whiteout' & Watermarking",
        "t2_desc": "Removes dark, cluttered warehouse backgrounds from phone photos and replaces them with a clean white background, complete with a custom WhatsApp watermark.",
        "t2_input_header": "Upload & Watermark Customization",
        "t2_file_label": "Upload warehouse raw photo (JPG, JPEG, PNG)",
        "t2_wm_header": "Advanced Watermark Options",
        "t2_wm_phone": "Watermark Phone Number",
        "t2_wm_apply": "Apply Customer Service Watermark",
        "t2_wm_qr": "Add WhatsApp QR Code Watermark",
        "t2_bg_method_label": "Background Clean Model / Service",
        "t2_wm_pos": "Watermark Position",
        "t2_wm_color": "Watermark Accent Color",
        "t2_wm_scale": "Watermark Font Size Ratio (%)",
        "t2_btn": "Start Cleaning Background",
        "t2_out_header": "Processing Result Preview",
        "t2_orig": "Uploaded Original Image",
        "t2_proc": "Cleared White-background Image",
        "t2_download": "Download Clean Image (JPG)",
        "t2_regenerate": "🔄 Regenerate",
        "t2_info": "Upload an image and click 'Start Cleaning Background'.",
        "t2_warn": "No image processed yet. Configure settings and click 'Start Cleaning Background'.",
        
        # Tab 3
        "t3_header": "WhatsApp Customer Service SOP Hub",
        "t3_desc": "Pre-configured responses for Nigerian customers, automatically replacing placeholders with your phone, address, and banking info.",
        "t3_setting_header": "Active Product Context for Chat",
        "t3_active_prod": "Current Product",
        "t3_active_price": "Negotiated Price (NGN)",
        "t3_active_moq": "Negotiated MOQ",
        "t3_subtab_price": "Price Inquiry Response",
        "t3_subtab_addr": "Warehouse Pickup Directions",
        "t3_subtab_moq": "Wholesale MOQ Rules",
        "t3_subtab_pay": "Official Account details",
        "t3_subtab_urg": "Urgent Scarcity Follow-up",
        "t3_mock_label": "Live WhatsApp Bubble Mockup:",
        
        # Tab 4
        "t4_header": "Chinese Video Script Localization Engine",
        "t4_desc": "Extracts structure from successful Chinese video transcripts (like weight challenges or direct container clearance) and localizes them into Nigerian shooting scripts.",
        "t4_input_header": "Input Video Copy Details",
        "t4_link_label": "Original Chinese Video Link (Optional context)",
        "t4_script_label": "Original Chinese Video Transcript (Required)",
        "t4_btn": "Run Script Reconstructor",
        "t4_out_header": "Localized Video Shooting Script",
        "t4_info": "Paste the Chinese script on the left, then click 'Run Script Reconstructor'.",
        
        # Tab 5
        "t5_header": "AI Social Ad Performance Pilot",
        "t5_desc": "Generates Meta (FB/IG) and TikTok targeting suggestions, copy variations, and indicators optimization guide for the product.",
        "t5_input_header": "Campaign Properties",
        "t5_channel_label": "Select Social Media Channels",
        "t5_budget_label": "Daily Testing Budget (USD)",
        "t5_btn": "Generate Ad Campaign Proposal",
        "t5_out_header": "Ads Campaign Setup Recommendation",
        "t5_info": "Click 'Generate Ad Campaign Proposal' to render targeting and copies.",
        
        # Tab 6
        "t6_header": "SOP Clearance Training Manual",
        "t6_desc": "Standard operating guide for e-commerce operators, customer service managers, and warehouse supervisors in Nigeria.",
        "t6_info": "Follow these rules closely to prevent local Nigerian bank transfer scams and lower COD delivery rejection rates.",
        "t6_exp1": "Stage 1: West African Traffic Funnel (TikTok & Meta Ads)",
        "t6_exp2": "Stage 2: Private Domain WhatsApp Group Building & Nurturing",
        "t6_exp3": "Stage 3: Cash on Delivery (COD) & Warehouse Fraud Prevention",
        "t6_exp4": "Stage 4: Customer Care Negotiation High-Conversion Script SOP"
    },
    "Nigerian Pidgin": {
        "title": "Sharp-Sharp AI Clearance System for Naija Warehouses",
        "subtitle": "One-stop control room to sell out your container loads of tyres, chairs, tables, and daily needs sharp-sharp! AI go write copy, clean your dark photos, give you WhatsApp replies, and Meta ads settings.",
        "sidebar_title": "Settings for System",
        "sidebar_info": "Anything you put here go automatically update all your ads copy, image watermark, WhatsApp reply, and payment bank account details.",
        "sidebar_api_key": "OpenAI API Key",
        "sidebar_api_key_help": "Put API Key to start GPT. If no key, system go run on Mock Mode showing samples.",
        "sidebar_base_url": "OpenAI API Base URL",
        "sidebar_model": "LLM Engine Model",
        "sidebar_contact_title": "Phone & Bank Details for Naija",
        "sidebar_phone": "WhatsApp Phone for Customer (Watermark & SOP)",
        "sidebar_address": "Lagos Warehouse Address for Self-Pickup",
        "sidebar_account_name": "Bank Account Name ( Sterling / GTB )",
        "sidebar_account_num": "Account Number & Bank Name",
        
        "tab_copy": "📢 Copywriter Sharp-Sharp",
        "tab_image": "🖼️ Clean Photo & Watermark",
        "tab_sop": "💬 WhatsApp SOP Hub (Copy-paste)",
        "tab_video": "🎬 Video Rebuilder for Naija",
        "tab_ads": "📈 Social Ad Pilot (Meta/TikTok)",
        "tab_training": "📚 Clearance SOP Manual Book",
        
        # Tab 1
        "t1_header": "Copywriter Sharp-Sharp for West Africa",
        "t1_desc": "AI go write 3 correct styles of pure English and Pidgin clearance copies that go make buyers pay sharp-sharp.",
        "t1_input_header": "Wetin you wan clear from warehouse?",
        "t1_cat": "Category for inside warehouse",
        "t1_name": "Product Name & Specs",
        "t1_price": "Chop life clearance price (NGN)",
        "t1_moq": "MOQ (Minimum buying quantity)",
        "t1_points": "Select correct features",
        "t1_extra": "Scarcity notice (e.g., Cargo dey finish!)",
        "t1_pidgin": "Spoil copy with correct Pidgin Slang",
        "t1_pidgin_help": "AI go insert 'Aje', 'Na double quality', 'No stories' inside your copy to sweet buyers.",
        "t1_btn": "Make AI write copy sharp-sharp",
        "t1_out_header": "Correct Clearance Copies (Pure English)",
        "t1_info": "Fill details for left, then click 'Make AI write copy sharp-sharp'.",
        "t1_mock_title": "Meta (Facebook/IG) Ad Visual Mockup for Phone",
        "t1_mock_desc": "See how your ad go look inside customer phone with the cleared white background photo:",
        "manage_expander": "🛠️ Manage Categories & Selling Points",
        "add_cat": "Add New Category",
        "del_cat": "Select Category to Delete",
        "add_pt": "Add New Selling Point",
        "del_pt": "Select Selling Point to Delete",
        "add_btn": "Add",
        "del_btn": "Delete",
        "dup_warn": "Dis thing dey already!",
        "empty_warn": "E no fit be empty!",
        "success_add_cat": "Category add & translate well-well: ",
        "success_del_cat": "Category delete successfully: ",
        "success_add_pt": "Feature add & translate well-well: ",
        "success_del_pt": "Feature delete successfully: ",
        
        # Tab 2
        "t2_header": "Photo background clean & Slap watermark",
        "t2_desc": "Remove dark, dirty backgrounds from warehouse phone pictures, make them clean white, and draw watermark capsule.",
        "t2_input_header": "Upload Photo & Choose Watermark",
        "t2_file_label": "Choose warehouse picture from phone (JPG, JPEG, PNG)",
        "t2_wm_header": "Watermark settings",
        "t2_wm_phone": "Phone for inside watermark",
        "t2_wm_apply": "Slap watermark on photo",
        "t2_wm_qr": "Slap WhatsApp QR Code on top",
        "t2_bg_method_label": "How to clean background / Model",
        "t2_wm_pos": "Watermark position",
        "t2_wm_color": "Watermark color theme",
        "t2_wm_scale": "Watermark text size (%)",
        "t2_btn": "Clean background & slap watermark",
        "t2_out_header": "Output Clean Picture",
        "t2_orig": "Photo from warehouse",
        "t2_proc": "Clean white background photo with watermark",
        "t2_download": "Download clean photo sharp-sharp (JPG)",
        "t2_regenerate": "🔄 Re-run process",
        "t2_info": "Upload photo and click 'Clean background & slap watermark'.",
        "t2_warn": "No photo clean yet. Put settings and click 'Clean background & slap watermark'.",
        
        # Tab 3
        "t3_header": "WhatsApp Customer SOP Hub (Copy & Paste)",
        "t3_desc": "WhatsApp shortcuts for customer service to reply buyers fast. System go replace phone and bank info automatically.",
        "t3_setting_header": "Current Chat product info",
        "t3_active_prod": "Wetin you dey discuss now",
        "t3_active_price": "Deal price (NGN)",
        "t3_active_moq": "MOQ deal",
        "t3_subtab_price": "Price & Stock Ask",
        "t3_subtab_addr": "Address & Direction",
        "t3_subtab_moq": "Why MOQ high?",
        "t3_subtab_pay": "Official Account Details",
        "t3_subtab_urg": "Scarcity Push & Booking Deposit",
        "t3_mock_label": "Phone Chat Screen Mockup:",
        
        # Tab 4
        "t4_header": "Chinese Video to Local Script Rebuilder",
        "t4_desc": "Translate Chinese viral script to high energy Pidgin English shooting script with video camera details.",
        "t4_input_header": "Input Chinese Copy text",
        "t4_link_label": "Chinese video link (Optional)",
        "t4_script_label": "Chinese video text voiceover (Required)",
        "t4_btn": "Translate & rebuild script",
        "t4_out_header": "Local Pidgin Shooting Script Table",
        "t4_info": "Paste Chinese text for left, click 'Translate & rebuild script'.",
        
        # Tab 5
        "t5_header": "Meta & TikTok Ads Pilot Hub",
        "t5_desc": "Get targeted interest words for Nigeria, ad copy varieties, and performance guide for Lagos market.",
        "t5_input_header": "Campaign setting",
        "t5_channel_label": "Select social channels",
        "t5_budget_label": "Daily budget (USD)",
        "t5_btn": "Get Campaign setup recommendation",
        "t5_out_header": "Targeting & Material setup recommendation",
        "t5_info": "Click 'Get Campaign setup recommendation' to view details.",
        
        # Tab 6
        "t6_header": "Warehouse Clearance SOP Manual Book",
        "t6_desc": "Learn how to get traffic, build WhatsApp groups, avoid fake transfer receipts, and secure Lagos local COD delivery.",
        "t6_info": "Do NOT deliver cargo to Abuja on COD. Lagos only! Verify bank balance in Sterling Bank app before releasing cargo.",
        "t6_exp1": "Stage 1: Meta/TikTok Ads Traffic secrets for Nigeria",
        "t6_exp2": "Stage 2: How to setup WhatsApp VIP clearance groups",
        "t6_exp3": "Stage 3: Prevent Fake Transfer SMS alert scams",
        "t6_exp4": "Stage 4: High conversion customer care chat rules"
    }
}

# Dynamically add missing translation keys to UI_LANG
UI_LANG["简体中文"]["glossary_title"] = "📖 附录：尼日利亚本土清仓黑话小贴士"
UI_LANG["简体中文"]["glossary_th_slang"] = "清仓黑话 (Pidgin)"
UI_LANG["简体中文"]["glossary_th_meaning"] = "英文释义 (English)"
UI_LANG["简体中文"]["glossary_th_purpose"] = "商业实操用途 (Purpose)"
UI_LANG["简体中文"]["t3_scen1"] = "场景一：客户发图询价及起批数量"
UI_LANG["简体中文"]["t3_scen2"] = "场景二：客户要求来仓自提或看货"
UI_LANG["简体中文"]["t3_scen3"] = "场景三：客户抱怨起批量太高"
UI_LANG["简体中文"]["t3_scen4"] = "场景四：向客户提供企业收款账号"
UI_LANG["简体中文"]["t3_scen5"] = "场景五：紧急催单与定金锁定"
UI_LANG["简体中文"]["t2_template_label"] = "增值营销排版模板 (Layout Template)"
UI_LANG["简体中文"]["t2_template_none"] = "无排版模板 (仅去噪与水印)"
UI_LANG["简体中文"]["t2_template_banner"] = "清仓大图海报横幅 (Clearance Banner)"
UI_LANG["简体中文"]["t2_template_stamp"] = "付款核对红色印章 (Official Paid Stamp)"
UI_LANG["简体中文"]["t2_price_label"] = "清仓单价 NGN"
UI_LANG["简体中文"]["t2_moq_label"] = "起批数量 PCS"

UI_LANG["English"]["glossary_title"] = "📖 Glossary: Nigeria Warehouse Selling Slang"
UI_LANG["English"]["glossary_th_slang"] = "Slang (Pidgin)"
UI_LANG["English"]["glossary_th_meaning"] = "English Meaning"
UI_LANG["English"]["glossary_th_purpose"] = "Commercial Purpose"
UI_LANG["English"]["t3_scen1"] = "Scenario 1: Customer asks for price and MOQ"
UI_LANG["English"]["t3_scen2"] = "Scenario 2: Customer wants warehouse self-pickup"
UI_LANG["English"]["t3_scen3"] = "Scenario 3: Customer complains MOQ is too high"
UI_LANG["English"]["t3_scen4"] = "Scenario 4: Customer asks for official bank details"
UI_LANG["English"]["t3_scen5"] = "Scenario 5: Urgent scarcity follow-up to lock stock"
UI_LANG["English"]["t2_template_label"] = "Marketing Layout Template"
UI_LANG["English"]["t2_template_none"] = "No Template (Watermark Only)"
UI_LANG["English"]["t2_template_banner"] = "Bottom Clearance Banner"
UI_LANG["English"]["t2_template_stamp"] = "Zenith Bank Paid Stamp"
UI_LANG["English"]["t2_price_label"] = "Clearance Price NGN"
UI_LANG["English"]["t2_moq_label"] = "MOQ in Pieces"

UI_LANG["Nigerian Pidgin"]["glossary_title"] = "📖 Glossary: Slang for inside Naija Warehouse"
UI_LANG["Nigerian Pidgin"]["glossary_th_slang"] = "Slang word (Pidgin)"
UI_LANG["Nigerian Pidgin"]["glossary_th_meaning"] = "Wetin e mean inside English"
UI_LANG["Nigerian Pidgin"]["glossary_th_purpose"] = "Wetin e dey do for business"
UI_LANG["Nigerian Pidgin"]["t3_scen1"] = "Scenario 1: Customer ask for price and MOQ rules"
UI_LANG["Nigerian Pidgin"]["t3_scen2"] = "Scenario 2: Customer wan come check warehouse directly"
UI_LANG["Nigerian Pidgin"]["t3_scen3"] = "Scenario 3: Customer complain say MOQ high too much"
UI_LANG["Nigerian Pidgin"]["t3_scen4"] = "Scenario 4: Customer ask for official bank details"
UI_LANG["Nigerian Pidgin"]["t3_scen5"] = "Scenario 5: Scarcity follow-up to collect deposit"
UI_LANG["Nigerian Pidgin"]["t2_template_label"] = "Marketing Layout Template"
UI_LANG["Nigerian Pidgin"]["t2_template_none"] = "No Template (Watermark only)"
UI_LANG["Nigerian Pidgin"]["t2_template_banner"] = "Down Wholesale Clearance Banner"
UI_LANG["Nigerian Pidgin"]["t2_template_stamp"] = "Zenith Bank Paid Stamp"
UI_LANG["Nigerian Pidgin"]["t2_price_label"] = "Clearance Price NGN"
UI_LANG["Nigerian Pidgin"]["t2_moq_label"] = "MOQ Quantity"

# ---------------------------------------------------------
# Sidebar Global Language Switcher
# ---------------------------------------------------------
sys_lang = st.sidebar.selectbox("🌐 Interface Language / 界面语言", ["简体中文", "English", "Nigerian Pidgin"], index=0)
L = UI_LANG[sys_lang]

# ---------------------------------------------------------
# Sidebar Global Configuration Center
# ---------------------------------------------------------
st.sidebar.markdown(f"## {L['sidebar_title']}")
st.sidebar.info(L["sidebar_info"])

# Load API keys from Streamlit secrets (for secure production deployment)
# or fallback to default credentials for out-of-the-box local testing.
try:
    openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
    openai_base_url = st.secrets.get("OPENAI_BASE_URL", "https://ai.baozinb.cn/v1")
    openai_model = st.secrets.get("OPENAI_MODEL", "gpt-5.5")
    openai_image_model = st.secrets.get("OPENAI_IMAGE_MODEL", "gpt-image-2")

    tencent_appid = st.secrets.get("TENCENT_APPID", "")
    tencent_secret_id = st.secrets.get("TENCENT_SECRET_ID", "")
    tencent_secret_key = st.secrets.get("TENCENT_SECRET_KEY", "")
    tencent_bucket = st.secrets.get("TENCENT_BUCKET", "")
    tencent_region = st.secrets.get("TENCENT_REGION", "ap-guangzhou")
except Exception:
    openai_api_key = ""
    openai_base_url = "https://ai.baozinb.cn/v1"
    openai_model = "gpt-5.5"
    openai_image_model = "gpt-image-2"

    tencent_appid = ""
    tencent_secret_id = ""
    tencent_secret_key = ""
    tencent_bucket = ""
    tencent_region = "ap-guangzhou"

# Clean up base url if it contains endpoint suffixes to prevent 404 errors
if openai_base_url:
    openai_base_url = openai_base_url.strip()
    for suffix in ["/images/generations", "/images/generations/", "/images/edits", "/images/edits/"]:
        if openai_base_url.endswith(suffix):
            openai_base_url = openai_base_url[:-len(suffix)]
            break

st.sidebar.markdown("---")

st.sidebar.markdown(f"### {L['sidebar_contact_title']}")

# Contact configs
watermark_phone = st.sidebar.text_input(L["sidebar_phone"], value="+86 15521176830")
lagos_address = st.sidebar.text_area(L["sidebar_address"], value="No 1 Wihu Avenue by enyo filling station Lagos Ibadan express way isheri -Oke Ogun state", height=68)
account_name = st.sidebar.text_area(L["sidebar_account_name"], value="Guangzhou Binfeng Trading Co., Ltd.", height=68)
account_number = st.sidebar.text_area(L["sidebar_account_num"], value="8810500194 - Sterling Bank PLC", height=68)

# ---------------------------------------------------------
# Initialize st.session_state variables
# ---------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "marketing_copy" not in st.session_state:
    st.session_state.marketing_copy = ""
if "processed_image" not in st.session_state:
    st.session_state.processed_image = None
if "processed_image_bytes" not in st.session_state:
    st.session_state.processed_image_bytes = None
if "rebuilt_script" not in st.session_state:
    st.session_state.rebuilt_script = ""
if "rebuilt_script_zh" not in st.session_state:
    st.session_state.rebuilt_script_zh = ""
if "rebuilt_script_en" not in st.session_state:
    st.session_state.rebuilt_script_en = ""
if "campaign_plan" not in st.session_state:
    st.session_state.campaign_plan = ""

if "t4_view" not in st.session_state:
    st.session_state.t4_view = "console"
if "t4_mode" not in st.session_state:
    st.session_state.t4_mode = "create"
if "t4_show_link" not in st.session_state:
    st.session_state.t4_show_link = False
if "t4_show_upload" not in st.session_state:
    st.session_state.t4_show_upload = False
if "t4_show_product_images" not in st.session_state:
    st.session_state.t4_show_product_images = False
if "t4_chat_history" not in st.session_state:
    st.session_state.t4_chat_history = []
if "t4_video_title" not in st.session_state:
    st.session_state.t4_video_title = ""
if "t4_input_visual_replicate" not in st.session_state:
    st.session_state.t4_input_visual_replicate = """我要复刻参考视频的运镜方式和节奏，不复制原产品。
请拆解参考视频的镜头、机位、动作、剪辑节奏，再改成我的产品拍摄分镜。"""
if "t4_scene" not in st.session_state:
    st.session_state.t4_scene = "Restaurant bar wooden table, warm indoor lighting"
if "t4_target_seconds" not in st.session_state:
    st.session_state.t4_target_seconds = 10
if "t4_video_analysis" not in st.session_state:
    st.session_state.t4_video_analysis = None
if "t4_video_montage_b64" not in st.session_state:
    st.session_state.t4_video_montage_b64 = ""
if "t4_output_lang" not in st.session_state:
    st.session_state.t4_output_lang = sys_lang
if "t4_input_analyze" not in st.session_state or "塑料椅子" in st.session_state.t4_input_analyze:
    st.session_state.t4_input_analyze = "从这个视频中提取完整的文本脚本，包括对话、旁白以及所有文字字幕："
if "t4_input_replicate" not in st.session_state or "大理石茶几" in st.session_state.t4_input_replicate:
    st.session_state.t4_input_replicate = "复刻这个视频的画面细节，包括画面构图、色彩、光影等："
if "t4_input_create" not in st.session_state or "Heavy Duty Plastic Stackable Chair" in st.session_state.t4_input_create:
    st.session_state.t4_input_create = """我希望创作的视频类型：[UGC种草/产品口播/产品演示/痛点-解决/前后对比/反应展示/故事讲述]
我的目标客群：[种族/地区/职业/生理特征等]
我的商品名称：
我的商品卖点：
我倾向的视频风格："""

if "t4_main_input" not in st.session_state or "塑料椅子" in st.session_state.t4_main_input or "大理石茶几" in st.session_state.t4_main_input or "Heavy Duty Plastic Stackable Chair" in st.session_state.t4_main_input:
    if st.session_state.get("t4_mode", "create") == "create":
        st.session_state.t4_main_input = st.session_state.t4_input_create
    elif st.session_state.get("t4_mode", "create") == "replicate":
        st.session_state.t4_main_input = st.session_state.t4_input_replicate
    else:
        st.session_state.t4_main_input = st.session_state.t4_input_analyze

T4_DEFAULT_INPUTS = {
    "简体中文": {
        "create": """我希望创作的视频类型：UGC种草
我的目标客群：尼日利亚的日常消费者
我的商品名称：
我的商品卖点：
我倾向的视频风格：""",
        "replicate": "复刻这个视频的画面细节，包括画面构图、色彩、光影等：",
        "analyze": "从这个视频中提取完整的文本脚本，包括对话、旁白以及所有文字字幕：",
        "visual_replicate": """我要复刻参考视频的运镜方式和节奏，不复制原产品。
请拆解参考视频的镜头、机位、动作、剪辑节奏，再改成我的产品拍摄分镜。""",
    },
    "English": {
        "create": """Video type I want to create: UGC product recommendation
Target audience: everyday Nigerian consumers
Product name:
Product selling points:
Preferred video style:""",
        "replicate": "Replicate this video's visual style, including composition, color, lighting, pacing, and camera movement:",
        "analyze": "Extract the full script from this video, including dialogue, narration, and all on-screen subtitles:",
        "visual_replicate": """I want to copy only the reference video's camera movement and editing rhythm, not its original product.
Break down the reference video's shots, camera positions, actions, and cut rhythm, then turn it into a storyboard for my own product.""",
    },
    "Nigerian Pidgin": {
        "create": """Video type wey I wan create: UGC product recommendation
Target people: everyday Nigerian buyers
Product name:
Main selling points:
Video style wey I want:""",
        "replicate": "Copy only this video's visual style: framing, color, light, pacing, and camera movement:",
        "analyze": "Bring out the full script from this video, including talk, voiceover, and every subtitle wey show for screen:",
        "visual_replicate": """I wan copy only the reference video's camera movement and editing rhythm, no copy the original product.
Break down the shots, camera position, action, and cut rhythm, then turn am to storyboard for my own product.""",
    },
}

if st.session_state.get("last_sys_lang") != sys_lang:
    defaults = T4_DEFAULT_INPUTS[sys_lang]
    st.session_state.t4_input_create = defaults["create"]
    st.session_state.t4_input_replicate = defaults["replicate"]
    st.session_state.t4_input_analyze = defaults["analyze"]
    st.session_state.t4_input_visual_replicate = defaults["visual_replicate"]
    st.session_state.t4_main_input = defaults.get(st.session_state.get("t4_mode", "create"), defaults["create"])
    st.session_state.last_sys_lang = sys_lang

if "status_message" not in st.session_state:
    st.session_state.status_message = None
if "active_prod" not in st.session_state:
    st.session_state.active_prod = "Heavy Duty Plastic Stackable Chair"
if "active_price" not in st.session_state:
    st.session_state.active_price = 12500
if "active_moq" not in st.session_state:
    st.session_state.active_moq = 50
if "prod_category" not in st.session_state:
    st.session_state.prod_category = "办公及家用桌椅 (Office & Home Furniture)"

if "t4_prod" not in st.session_state:
    st.session_state.t4_prod = "Heavy Duty Plastic Stackable Chair"
if "t4_price" not in st.session_state:
    st.session_state.t4_price = 12500
if "t4_moq" not in st.session_state:
    st.session_state.t4_moq = 50

# Global state references for cross-tab availability
active_prod = st.session_state.active_prod
active_price = st.session_state.active_price
active_moq = st.session_state.active_moq
prod_category = st.session_state.prod_category# ---------------------------------------------------------
# Configuration Persistence Logic
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_config.json")

def save_persistent_data():
    try:
        data = {
            "categories_dict": st.session_state.categories_dict,
            "points_dict": st.session_state.points_dict,
            "points_defaults": st.session_state.points_defaults
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Failed to save configuration: {e}")

def load_persistent_data():
    default_categories = {
        "简体中文": [
            "汽车配件与轮胎 (Auto Parts & Tires)",
            "办公及家用桌椅 (Office & Home Furniture)",
            "塑料制品与日用杂货 (Plastic Ware & Daily Sundries)",
            "家用电器 (Home Appliances)",
            "五金与建材工具 (Hardware & Building Materials)",
            "其他杂品清仓 (Other Clearing Items)"
        ],
        "English": [
            "Auto Parts & Tires",
            "Office & Home Furniture",
            "Plastic Ware & Daily Sundries",
            "Home Appliances",
            "Hardware & Building Materials",
            "Other Clearance Items"
        ],
        "Nigerian Pidgin": [
            "Tyres & Auto Parts",
            "Office & Home Chairs/Tables",
            "Plastics & House Sundries",
            "Home Appliances",
            "Hardware & Building tools",
            "Other Clearance Cargo"
        ]
    }
    
    default_points = {
        "简体中文": [
            "货到付款 (Cash on Delivery / COD)",
            "拉各斯本土仓库现场看货/自提 (Lagos Warehouse Pick-up)",
            "源头清仓超低价 (Direct Importer Wholesale Price)",
            "集装箱刚刚到港 (Fresh Container Landing)",
            "极致坚固耐用 (Heavy Duty & Super Durable)",
            "库存告急先到先得 (Limited Stock, First Come First Served)"
        ],
        "English": [
            "Cash on Delivery / COD",
            "Lagos Warehouse Self-Pickup",
            "Direct Importer Price",
            "Fresh Container Landing",
            "Super Durable / Heavy Duty",
            "Limited Stock / First Come First Served"
        ],
        "Nigerian Pidgin": [
            "Cash on Delivery (COD) allowed",
            "Lagos warehouse pickup sharp-sharp",
            "Direct Importer wholesale price",
            "Container just land now-now",
            "Na double quality - solid scatter",
            "First come first serve - Stock dey clear"
        ]
    }
    
    default_defaults = {
        "简体中文": [
            "货到付款 (Cash on Delivery / COD)", 
            "拉各斯本土仓库现场看货/自提 (Lagos Warehouse Pick-up)", 
            "源头清仓超低价 (Direct Importer Wholesale Price)", 
            "极致坚固耐用 (Heavy Duty & Super Durable)"
        ],
        "English": [
            "Cash on Delivery / COD",
            "Lagos Warehouse Self-Pickup",
            "Direct Importer Price",
            "Super Durable / Heavy Duty"
        ],
        "Nigerian Pidgin": [
            "Cash on Delivery (COD) allowed",
            "Lagos warehouse pickup sharp-sharp",
            "Direct Importer wholesale price",
            "Na double quality - solid scatter"
        ]
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.categories_dict = data.get("categories_dict", default_categories)
                st.session_state.points_dict = data.get("points_dict", default_points)
                st.session_state.points_defaults = data.get("points_defaults", default_defaults)
                return
        except Exception:
            pass
            
    st.session_state.categories_dict = default_categories
    st.session_state.points_dict = default_points
    st.session_state.points_defaults = default_defaults
    save_persistent_data()

load_persistent_data()

def inject_custom_css():
    st.markdown("""
    <style>
        /* Google Fonts & Icons CDN */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

        /* Pentagram Aesthetic Stylesheet */
        :root {
            --bg-color: #060913;
            --card-bg: rgba(13, 19, 36, 0.7);
            --card-border: rgba(0, 242, 254, 0.15);
            --card-border-hover: rgba(124, 58, 237, 0.45);
            --text-primary: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #00F2FE;
            --accent-purple: #7C3AED;
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Inter', sans-serif;
            
            /* 8px Vertical Rhythm Spacing Scale */
            --space-1: 4px;
            --space-2: 8px;
            --space-3: 12px;
            --space-4: 16px;
            --space-6: 24px;
            --space-8: 32px;
            --space-12: 48px;
            --space-16: 64px;
        }

        .main {
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
            background-image: radial-gradient(rgba(0, 242, 254, 0.035) 1px, transparent 1px) !important;
            background-size: 32px 32px !important;
        }
        
        .block-container {
            padding-top: var(--space-4) !important;
            padding-bottom: var(--space-16) !important;
            padding-left: var(--space-8) !important;
            padding-right: var(--space-8) !important;
            max-width: 1440px !important;
            margin: 0 auto !important;
        }
        
        html, body, [class*="css"], .stMarkdown {
            font-family: var(--font-body), -apple-system, sans-serif !important;
        }
        
        h1, h2, h3, h4, h5, h6, .header-title, .card-header {
            font-family: var(--font-display), sans-serif !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #090e1a !important;
            border-right: 1px solid rgba(0, 242, 254, 0.08) !important;
        }
        
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            font-family: var(--font-display) !important;
            color: #FFFFFF !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox label, 
        section[data-testid="stSidebar"] .stTextInput label, 
        section[data-testid="stSidebar"] .stTextArea label {
            color: var(--text-muted) !important;
        }

        /* Form elements adaptation to dark theme */
        .stSelectbox div[data-baseweb="select"], 
        .stTextInput input, 
        .stTextArea textarea, 
        .stNumberInput input, 
        .stMultiSelect div[role="combobox"] {
            background-color: #0d1324 !important;
            border: 1px solid rgba(0, 242, 254, 0.18) !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            font-family: var(--font-body) !important;
            transition: all 0.25s ease !important;
        }

        .stSelectbox div[data-baseweb="select"]:hover, 
        .stTextInput input:hover, 
        .stTextArea textarea:hover, 
        .stNumberInput input:hover, 
        .stMultiSelect div[role="combobox"]:hover {
            border-color: var(--accent-cyan) !important;
            box-shadow: 0 0 8px rgba(0, 242, 254, 0.15) !important;
        }

        .stTextInput input:focus, 
        .stTextArea textarea:focus, 
        .stNumberInput input:focus {
            border-color: var(--accent-cyan) !important;
            box-shadow: 0 0 12px rgba(0, 242, 254, 0.3) !important;
            background-color: #090e1a !important;
        }

        /* Multiselect tags */
        div[data-baseweb="tag"] {
            background-color: rgba(124, 58, 237, 0.18) !important;
            border: 1px solid rgba(124, 58, 237, 0.4) !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            padding: 2px 8px !important;
        }
        div[data-baseweb="tag"] span {
            color: #FFFFFF !important;
            font-family: var(--font-body) !important;
            font-size: 0.85rem !important;
        }
        div[data-baseweb="tag"] div[role="button"] {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        div[data-baseweb="tag"] div[role="button"]:hover {
            color: #FFFFFF !important;
            background-color: rgba(124, 58, 237, 0.3) !important;
        }

        /* Hero Banner Styles */
        .hero-container {
            position: relative;
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.05) 0%, rgba(124, 58, 237, 0.05) 100%);
            border: 1px solid rgba(0, 242, 254, 0.15);
            border-radius: 24px;
            padding: var(--space-8) var(--space-8);
            margin-bottom: var(--space-6);
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .hero-grid-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: radial-gradient(rgba(0, 242, 254, 0.1) 1.5px, transparent 1.5px);
            background-size: 24px 24px;
            pointer-events: none;
            opacity: 0.65;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: var(--accent-cyan);
            font-family: var(--font-display);
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 2px;
            margin-bottom: var(--space-3);
            text-transform: uppercase;
        }

        .hero-badge .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--accent-cyan);
            box-shadow: 0 0 8px var(--accent-cyan);
        }

        .hero-title {
            font-size: 3.2rem;
            font-weight: 800;
            line-height: 1.2;
            color: #FFFFFF;
            letter-spacing: -1px;
            margin-bottom: var(--space-3);
        }

        .gradient-text {
            background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            line-height: 1.8;
            color: var(--text-muted);
            max-width: 850px;
            margin: 0;
        }

        /* Modern Glassmorphic Card layouts using native containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: var(--card-bg) !important;
            backdrop-filter: blur(16px);
            border: 1px solid var(--card-border) !important;
            padding: var(--space-4) !important;
            border-radius: 16px !important;
            margin-bottom: var(--space-4) !important;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7) !important;
            position: relative;
            overflow: hidden;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        /* Top accent bar for cards */
        div[data-testid="stVerticalBlockBorderWrapper"]::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
            z-index: 10;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-4px);
            border-color: var(--card-border-hover) !important;
            box-shadow: 0 20px 40px -15px rgba(124, 58, 237, 0.25) !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] h3 {
            font-family: var(--font-display) !important;
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            margin-top: 0px !important;
            margin-bottom: 20px !important;
            border-bottom: 1px solid rgba(0, 242, 254, 0.15) !important;
            padding-bottom: 10px !important;
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
        }
        
        /* Widget labels - Bigger & High Contrast */
        .stSelectbox label, 
        .stTextInput label, 
        .stTextArea label, 
        .stNumberInput label, 
        .stMultiSelect label, 
        .stSlider label {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: #E2E8F0 !important;
            margin-bottom: var(--space-2) !important;
        }

        /* Make code blocks auto-wrap text and hide horizontal scrollbar */
        div[data-testid="stCodeBlock"] pre, 
        div[data-testid="stCodeBlock"] code,
        pre, code {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
        }

        
        /* Secondary Button (Default) */
        .stButton>button {
            background-color: rgba(13, 19, 36, 0.6) !important;
            color: var(--text-primary) !important;
            border: 1px solid rgba(0, 242, 254, 0.2) !important;
            font-family: var(--font-body) !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            padding: 0.5rem 1.2rem !important;
            border-radius: 8px !important;
            transition: all 0.25s ease !important;
            box-shadow: none !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            border-color: var(--accent-cyan) !important;
            color: var(--accent-cyan) !important;
            background-color: rgba(0, 242, 254, 0.05) !important;
        }

        .stButton>button:active {
            transform: scale(0.98) !important;
        }

        /* Primary Button (Main Action / Glow) */
        .stButton>button[kind="primary"] {
            background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-purple) 100%) !important;
            color: #060913 !important;
            border: none !important;
            font-family: var(--font-display) !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.65rem 1.5rem !important;
            border-radius: 10px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.25) !important;
            width: 100% !important;
        }

        .stButton>button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 242, 254, 0.45) !important;
            color: #FFFFFF !important;
        }

        /* Navbar wrapper styling */
        .navbar-wrapper {
            margin-bottom: var(--space-6);
            background-color: rgba(13, 19, 36, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 242, 254, 0.1);
            border-radius: 16px;
            padding: 8px 16px;
        }

        .nav-logo {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: 1px;
            height: 100%;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 4px;
        }

        /* Custom Top Navigation Button Overrides */
        .navbar-wrapper div[data-testid*="stBaseButton-nav_btn_"] button {
            background: transparent !important;
            color: var(--text-muted) !important;
            border: 1px solid transparent !important;
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 6px 12px !important;
            border-radius: 8px !important;
            transition: all 0.25s ease !important;
            box-shadow: none !important;
            width: 100% !important;
            white-space: nowrap !important;
            height: 38px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
        }

        .navbar-wrapper div[data-testid*="stBaseButton-nav_btn_"] button:hover {
            color: var(--accent-cyan) !important;
            background-color: rgba(0, 242, 254, 0.08) !important;
            border-color: rgba(0, 242, 254, 0.2) !important;
            transform: none !important;
        }

        /* Align columns vertically inside navbar */
        .navbar-wrapper div[data-testid="column"] {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Custom Card inner styles */
        .card-badge {
            color: var(--accent-cyan);
            font-family: var(--font-display);
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        
        .card-subtitle-sub {
            color: var(--text-muted);
            font-family: var(--font-body);
            font-size: 0.8rem;
            margin-bottom: 12px;
        }

        .card-title-main {
            font-family: var(--font-display);
            font-size: 1.35rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 12px;
            margin-top: 0px;
            min-height: 64px; /* Uniform height for 1 or 2 lines of text */
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-desc-text {
            color: var(--text-muted);
            font-size: 0.88rem;
            line-height: 1.6;
            margin-bottom: 20px;
            height: 96px; /* Uniform height for description text on 8px vertical rhythm */
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
        }

        /* Equal height grid layout for Streamlit columns containing cards */
        div[data-testid="column"]:has(.card-desc-text) {
            display: flex !important;
            flex-direction: column !important;
            justify-content: stretch !important;
        }

        div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-desc-text) {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
            height: 100% !important;
        }

        /* Push button container to the bottom of the card */
        div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-desc-text) > div[data-testid="element-container"]:last-child {
            margin-top: auto !important;
            padding-top: var(--space-4) !important;
        }

        /* WhatsApp Chat Simulator */
        .whatsapp-container {
            background-color: #0d1418;
            border-radius: 16px;
            border: 1px solid #222f3e;
            overflow: hidden;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
            max-width: 480px;
            margin: 20px auto;
            font-family: var(--font-body);
        }
        .whatsapp-header {
            background-color: #075e54;
            color: white;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: bold;
            border-bottom: 1px solid #054c44;
        }
        .whatsapp-avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background-color: #128c7e;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            color: white;
        }
        .whatsapp-header-info {
            display: flex;
            flex-direction: column;
        }
        .whatsapp-header-name {
            font-size: 0.95rem;
            font-weight: 600;
        }
        .whatsapp-header-status {
            font-size: 0.75rem;
            color: #8ce4dc;
            font-weight: normal;
        }
        .whatsapp-body {
            background-color: #0b141a;
            background-image: radial-gradient(#152026 1px, transparent 1px);
            background-size: 15px 15px;
            padding: 20px;
            min-height: 240px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }
        .whatsapp-msg {
            max-width: 82%;
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 0.9rem;
            line-height: 1.45;
            word-wrap: break-word;
        }
        .whatsapp-msg-in {
            background-color: #202c33;
            color: #e9edef;
            align-self: flex-start;
            border-top-left-radius: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }
        .whatsapp-msg-out {
            background-color: #005c4b;
            color: #e9edef;
            align-self: flex-end;
            border-top-right-radius: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }
        
        /* Facebook Ad Card Simulator */
        .fb-ad-container {
            background-color: #18191a;
            border: 1px solid #2d2f30;
            border-radius: 14px;
            padding: 16px;
            max-width: 500px;
            margin: 20px auto;
            font-family: var(--font-body);
            color: #e4e6eb;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }
        .fb-ad-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
        }
        .fb-ad-avatar {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
            color: white;
        }
        .fb-ad-header-text {
            display: flex;
            flex-direction: column;
        }
        .fb-ad-name {
            font-weight: 700;
            font-size: 0.95rem;
            color: #e4e6eb;
        }
        .fb-ad-meta {
            font-size: 0.78rem;
            color: #b0b3b8;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .fb-ad-text {
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 14px;
            white-space: pre-wrap;
            color: #e4e6eb;
        }
        .fb-ad-media {
            background-color: #242526;
            border: 1px solid #2d2f30;
            border-radius: 8px;
            overflow: hidden;
            text-align: center;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .fb-ad-media img {
            width: 100%;
            max-height: 300px;
            object-fit: contain;
        }
        .fb-ad-footer-bar {
            background-color: #242526;
            padding: 12px 14px;
            border-top: 1px solid #2d2f30;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px;
        }
        .fb-ad-footer-left {
            display: flex;
            flex-direction: column;
            gap: 3px;
            max-width: 70%;
        }
        .fb-ad-caption {
            font-size: 0.72rem;
            color: #b0b3b8;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        .fb-ad-headline {
            font-weight: 700;
            font-size: 0.92rem;
            color: #e4e6eb;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .fb-ad-btn {
            background-color: #3a3b3c;
            color: #e4e6eb;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            text-decoration: none;
            border: 1px solid #4e4f50;
            transition: all 0.2s;
        }
        .fb-ad-btn:hover {
            background-color: #4e4f50;
            color: white;
            border-color: var(--accent-cyan);
        }

        /* High Density Premium Tables */
        .stMarkdown table {
            width: 100% !important;
            border-collapse: collapse !important;
            margin: 16px 0 !important;
            font-family: var(--font-body) !important;
            font-size: 0.9rem !important;
            background-color: rgba(13, 19, 36, 0.4) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        .stMarkdown th {
            background-color: rgba(0, 242, 254, 0.08) !important;
            color: var(--accent-cyan) !important;
            font-weight: 600 !important;
            text-align: left !important;
            padding: 10px 14px !important;
            border-bottom: 2px solid rgba(0, 242, 254, 0.2) !important;
            text-transform: uppercase !important;
            font-size: 0.8rem !important;
            letter-spacing: 0.5px !important;
        }
        
        .stMarkdown td {
            padding: 10px 14px !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
            color: #e2e8f0 !important;
            line-height: 1.5 !important;
        }
        
        .stMarkdown tr:hover {
            background-color: rgba(0, 242, 254, 0.02) !important;
        }
        
        .stMarkdown tr:last-child td {
            border-bottom: none !important;
        }

        /* Slider styling */
        div[data-testid="stSlider"] div[role="slider"] {
            background-color: var(--accent-cyan) !important;
            border: 2px solid #FFFFFF !important;
            box-shadow: 0 0 8px var(--accent-cyan) !important;
            width: 16px !important;
            height: 16px !important;
            top: -4px !important;
        }
        div[data-testid="stSlider"] div[role="presentation"] > div {
            background-color: rgba(0, 242, 254, 0.3) !important;
        }

        /* Expander styling */
        div[data-testid="stExpander"] {
            background-color: rgba(13, 19, 36, 0.4) !important;
            border: 1px solid rgba(0, 242, 254, 0.1) !important;
            border-radius: 8px !important;
            margin-bottom: 12px !important;
            transition: all 0.25s ease !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(0, 242, 254, 0.2) !important;
            background-color: rgba(13, 19, 36, 0.6) !important;
        }
        div[data-testid="stExpander"] summary {
            font-family: var(--font-display) !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }
        div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
            padding: 16px !important;
            background-color: rgba(6, 9, 19, 0.5) !important;
            border-top: 1px solid rgba(0, 242, 254, 0.05) !important;
        }

        /* Space out sidebar elements for breathing room */
        section[data-testid="stSidebar"] div.stTextArea,
        section[data-testid="stSidebar"] div.stTextInput {
            margin-bottom: 24px !important;
        }

        /* Creatok.ai-Style Video Rebuilder CSS */
        .creatok-badge {
            background-color: rgba(0, 242, 254, 0.12) !important;
            border: 1px solid rgba(0, 242, 254, 0.3) !important;
            color: var(--accent-cyan) !important;
            padding: 4px 10px !important;
            border-radius: 99px !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            text-transform: uppercase !important;
            margin-bottom: 12px !important;
        }

        .creatok-console {
            background-color: rgba(13, 19, 36, 0.7) !important;
            border: 1px solid rgba(0, 242, 254, 0.15) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4) !important;
            margin-bottom: 30px !important;
        }

        .creatok-pills-row {
            display: flex !important;
            gap: 12px !important;
            margin-bottom: 16px !important;
            flex-wrap: wrap !important;
        }

        .creatok-pill {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #94a3b8 !important;
            padding: 6px 14px !important;
            border-radius: 99px !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
        }

        .creatok-pill-active {
            background-color: rgba(0, 242, 254, 0.1) !important;
            border-color: var(--accent-cyan) !important;
            color: var(--accent-cyan) !important;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
        }

        .creatok-pill:hover {
            border-color: rgba(0, 242, 254, 0.4) !important;
            color: #ffffff !important;
        }

        .history-item-row {
            background-color: rgba(13, 19, 36, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
            transition: all 0.25s ease !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }

        .history-item-row:hover {
            background-color: rgba(0, 242, 254, 0.05) !important;
            border-color: rgba(0, 242, 254, 0.3) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(0, 242, 254, 0.1) !important;
        }

        .history-item-left {
            display: flex !important;
            align-items: center !important;
            gap: 14px !important;
        }

        .history-item-icon {
            width: 36px !important;
            height: 36px !important;
            border-radius: 50% !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #94a3b8 !important;
        }

        .history-item-row:hover .history-item-icon {
            background-color: rgba(0, 242, 254, 0.15) !important;
            color: var(--accent-cyan) !important;
        }

        .history-item-title {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }

        .history-item-time {
            font-size: 0.78rem !important;
            color: #64748b !important;
        }

        /* Video Player Card Preview */
        .video-player-card {
            background-color: rgba(13, 19, 36, 0.6) !important;
            border: 1px solid rgba(0, 242, 254, 0.2) !important;
            border-radius: 16px !important;
            overflow: hidden !important;
            margin-bottom: 24px !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
        }

        .video-player-display {
            background-color: #000000 !important;
            height: 200px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            color: rgba(255,255,255,0.7) !important;
            position: relative !important;
            background-image: radial-gradient(rgba(0, 242, 254, 0.05) 1px, transparent 1px) !important;
            background-size: 20px 20px !important;
        }

        .video-play-btn {
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #060913 !important;
            font-size: 1.5rem !important;
            box-shadow: 0 0 15px var(--accent-cyan) !important;
            margin-bottom: 10px !important;
            cursor: pointer !important;
        }

        .video-player-meta {
            padding: 14px 18px !important;
            background-color: rgba(6, 9, 19, 0.8) !important;
            border-top: 1px solid rgba(255,255,255,0.05) !important;
        }

        .video-meta-link {
            font-size: 0.8rem !important;
            color: var(--accent-cyan) !important;
            word-break: break-all !important;
            margin: 0 !important;
        }

        /* Timeline analysis storyboard steps */
        .timeline-step {
            position: relative !important;
            padding-left: 28px !important;
            border-left: 2px solid rgba(0, 242, 254, 0.15) !important;
            margin-bottom: 24px !important;
            padding-bottom: 8px !important;
        }

        .timeline-step-last {
            border-left: 2px solid transparent !important;
        }

        .timeline-marker {
            position: absolute !important;
            left: -9px !important;
            top: 2px !important;
            width: 16px !important;
            height: 16px !important;
            border-radius: 50% !important;
            background-color: #060913 !important;
            border: 3px solid var(--accent-cyan) !important;
            box-shadow: 0 0 8px var(--accent-cyan) !important;
        }

        .timeline-time {
            font-family: var(--font-display) !important;
            font-size: 0.82rem !important;
            color: var(--accent-cyan) !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            margin-bottom: 6px !important;
            text-transform: uppercase !important;
        }

        .timeline-title {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin-bottom: 10px !important;
        }

        .timeline-content-box {
            background-color: rgba(13, 19, 36, 0.5) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 10px !important;
            padding: 14px !important;
            font-size: 0.9rem !important;
            line-height: 1.5 !important;
        }

        /* Follow-up chat styling */
        .chat-bubble {
            padding: 12px 16px !important;
            border-radius: 12px !important;
            margin-bottom: 14px !important;
            max-width: 85% !important;
            font-size: 0.92rem !important;
            line-height: 1.5 !important;
            word-wrap: break-word !important;
        }

        .chat-bubble-assistant {
            background-color: rgba(13, 19, 36, 0.7) !important;
            border: 1px solid rgba(0, 242, 254, 0.1) !important;
            color: #f8fafc !important;
            align-self: flex-start !important;
            border-top-left-radius: 0px !important;
        }

        .chat-bubble-user {
            background-color: rgba(124, 58, 237, 0.15) !important;
            border: 1px solid rgba(124, 58, 237, 0.3) !important;
            color: #f8fafc !important;
            align-self: flex-end !important;
            border-top-right-radius: 0px !important;
            margin-left: auto !important;
        }
    </style>
    <script>
        (function() {
            const adjustHeight = (el) => {
                const scrollH = el.scrollHeight;
                if (scrollH > 0 && el.offsetHeight !== scrollH) {
                    // Set height with extra 24px buffer (one line height space)
                    el.style.setProperty('height', (scrollH + 24) + 'px', 'important');
                }
            };
            
            const initTextareas = () => {
                const textareas = document.querySelectorAll('section[data-testid="stSidebar"] textarea');
                textareas.forEach(ta => {
                    adjustHeight(ta);
                    if (!ta.dataset.observed) {
                        ta.dataset.observed = 'true';
                        ta.addEventListener('input', () => {
                            ta.style.setProperty('height', 'auto', 'important');
                            adjustHeight(ta);
                        });
                    }
                });
            };
            
            // Periodically check and auto-expand all sidebar textareas
            setInterval(initTextareas, 400);
        })();
    </script>
    """, unsafe_allow_html=True)

# Helper to base64 encode PIL Image for HTML Rendering
def get_base64_image(image):
    if image is None:
        return ""
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    except Exception:
        return ""

# ---------------------------------------------------------
# Application Helper Functions & Mock Data Generators
# ---------------------------------------------------------

def extract_llm_response(response):
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        try:
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if isinstance(choice, dict):
                    if "message" in choice and isinstance(choice["message"], dict):
                        return choice["message"].get("content", "")
                    return choice.get("text", "")
            return str(response)
        except Exception:
            return str(response)
    try:
        if hasattr(response, "choices") and len(response.choices) > 0:
            return response.choices[0].message.content
    except Exception:
        pass
    return str(response)

def _call_openai(system_prompt, user_prompt, temperature=0.7):
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
    response = client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        stream=True
    )
    content = ""
    for chunk in response:
        if hasattr(chunk, "choices") and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                content += delta.content
    return content

def generate_image_gpt_image_2(user_prompt, ref_image_bytes=None):
    from openai import OpenAI
    import base64
    import io
    from PIL import Image
    
    client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
    
    final_prompt = user_prompt
    
    # If reference image is provided, use LLM with vision to generate combined prompt
    if ref_image_bytes:
        base64_image = base64.b64encode(ref_image_bytes).decode('utf-8')
        try:
            # We use openai_model for chat completion with image input, specifying stream=True
            response = client.chat.completions.create(
                model=openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional AI image prompt engineer. Describe the product/clothing in the image in detail (color, style, textures, cut) and seamlessly integrate it into the user's scene description to build a highly detailed prompt for DALL-E/gpt-image-2. Output ONLY the prompt in English."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"User prompt: {user_prompt}\n\nPlease generate a unified detailed image prompt describing the product/clothing in this image placed in the user's scene."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                stream=True
            )
            content = ""
            for chunk in response:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        content += delta.content
            llm_prompt = content.strip()
            if llm_prompt:
                final_prompt = llm_prompt
        except Exception as vision_err:
            pass
            
    # Call image generation or editing API
    if ref_image_bytes:
        try:
            image = Image.open(io.BytesIO(ref_image_bytes)).convert("RGBA")
            image_resized = image.resize((1024, 1024), Image.Resampling.LANCZOS)
            
            img_byte_arr = io.BytesIO()
            image_resized.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Fully transparent mask of 1024x1024
            mask_image = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
            mask_byte_arr = io.BytesIO()
            mask_image.save(mask_byte_arr, format='PNG')
            mask_bytes = mask_byte_arr.getvalue()
            
            img_response = client.images.edit(
                model=openai_image_model if openai_image_model else "gpt-image-2",
                image=("image.png", img_bytes, "image/png"),
                mask=("mask.png", mask_bytes, "image/png"),
                prompt=final_prompt,
                n=1,
                size="1024x1024"
            )
        except Exception as edit_err:
            raise edit_err
    else:
        try:
            img_response = client.images.generate(
                model=openai_image_model if openai_image_model else "gpt-image-2",
                prompt=final_prompt,
                n=1,
                size="1024x1024"
            )
        except Exception as gen_err:
            raise gen_err
            
    img_data = img_response.data[0]
    if hasattr(img_data, "url") and img_data.url:
        return img_data.url, final_prompt, False
    elif hasattr(img_data, "b64_json") and img_data.b64_json:
        return img_data.b64_json, final_prompt, True
    else:
        raise ValueError("No image URL or b64_json found in response.")

def call_llm(system_prompt, user_prompt, mock_func):
    if not openai_api_key:
        return mock_func()
    try:
        content = _call_openai(system_prompt, user_prompt, temperature=0.7)
        return content if content else mock_func()
    except Exception as e:
        st.error(f"AI API Error: {e}")
        return mock_func()

def _image_to_data_url(image_source, max_size=(1024, 1024)):
    try:
        if isinstance(image_source, Image.Image):
            image = image_source.convert("RGB")
        else:
            image = Image.open(image_source).convert("RGB")
        image.thumbnail(max_size)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=86)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}"
    except Exception:
        return ""

def call_llm_with_images(system_prompt, user_prompt, image_sources, mock_func):
    if not openai_api_key:
        return mock_func()
    valid_images = []
    for image_source in image_sources or []:
        data_url = _image_to_data_url(image_source)
        if data_url:
            valid_images.append(data_url)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
        content_parts = [{"type": "text", "text": user_prompt}]
        for data_url in valid_images[:8]:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": data_url}
            })
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_parts}
            ],
            temperature=0.7,
            stream=True
        )
        content = ""
        for chunk in response:
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    content += delta.content
        return content if content else mock_func()
    except Exception as e:
        st.error(f"AI Vision API Error: {e}")
        return mock_func()

def split_bilingual_script(content):
    if not content:
        return "", ""
    zh_markers = ["[[ZH]]", "【中文】", "### 中文", "# 中文"]
    en_markers = ["[[EN]]", "【ENGLISH】", "### English", "# English"]
    zh_pos = -1
    zh_marker = ""
    en_pos = -1
    en_marker = ""
    for marker in zh_markers:
        pos = content.find(marker)
        if pos >= 0 and (zh_pos < 0 or pos < zh_pos):
            zh_pos = pos
            zh_marker = marker
    for marker in en_markers:
        pos = content.find(marker)
        if pos >= 0 and (en_pos < 0 or pos < en_pos):
            en_pos = pos
            en_marker = marker
    if zh_pos >= 0 and en_pos >= 0:
        if zh_pos < en_pos:
            zh = content[zh_pos + len(zh_marker):en_pos].strip()
            en = content[en_pos + len(en_marker):].strip()
        else:
            en = content[en_pos + len(en_marker):zh_pos].strip()
            zh = content[zh_pos + len(zh_marker):].strip()
        return zh, en
    return content.strip(), ""

def translate_text(text, target_lang):
    """
    Translates a short string (category/selling point) to the target language.
    Utilizes LLM if API key is provided, otherwise falls back to a simple dictionary or returns the text.
    """
    if not text or not text.strip():
        return ""
    
    # Clean text to make dictionary lookup more robust
    text_clean = text.strip()
    
    # Offline dictionary mapping for initial values and fallback
    dict_map = {
        # Categories
        "汽车配件与轮胎 (Auto Parts & Tires)": {
            "简体中文": "汽车配件与轮胎 (Auto Parts & Tires)",
            "English": "Auto Parts & Tires",
            "Nigerian Pidgin": "Tyres & Auto Parts"
        },
        "Auto Parts & Tires": {
            "简体中文": "汽车配件与轮胎 (Auto Parts & Tires)",
            "English": "Auto Parts & Tires",
            "Nigerian Pidgin": "Tyres & Auto Parts"
        },
        "Tyres & Auto Parts": {
            "简体中文": "汽车配件与轮胎 (Auto Parts & Tires)",
            "English": "Auto Parts & Tires",
            "Nigerian Pidgin": "Tyres & Auto Parts"
        },
        "办公及家用桌椅 (Office & Home Furniture)": {
            "简体中文": "办公及家用桌椅 (Office & Home Furniture)",
            "English": "Office & Home Furniture",
            "Nigerian Pidgin": "Office & Home Chairs/Tables"
        },
        "Office & Home Furniture": {
            "简体中文": "办公及家用桌椅 (Office & Home Furniture)",
            "English": "Office & Home Furniture",
            "Nigerian Pidgin": "Office & Home Chairs/Tables"
        },
        "Office & Home Chairs/Tables": {
            "简体中文": "办公及家用桌椅 (Office & Home Furniture)",
            "English": "Office & Home Furniture",
            "Nigerian Pidgin": "Office & Home Chairs/Tables"
        },
        "塑料制品与日用杂货 (Plastic Ware & Daily Sundries)": {
            "简体中文": "塑料制品与日用杂货 (Plastic Ware & Daily Sundries)",
            "English": "Plastic Ware & Daily Sundries",
            "Nigerian Pidgin": "Plastics & House Sundries"
        },
        "Plastic Ware & Daily Sundries": {
            "简体中文": "塑料制品与日用杂货 (Plastic Ware & Daily Sundries)",
            "English": "Plastic Ware & Daily Sundries",
            "Nigerian Pidgin": "Plastics & House Sundries"
        },
        "Plastics & House Sundries": {
            "简体中文": "塑料制品与日用杂货 (Plastic Ware & Daily Sundries)",
            "English": "Plastic Ware & Daily Sundries",
            "Nigerian Pidgin": "Plastics & House Sundries"
        },
        "家用电器 (Home Appliances)": {
            "简体中文": "家用电器 (Home Appliances)",
            "English": "Home Appliances",
            "Nigerian Pidgin": "Home Appliances"
        },
        "Home Appliances": {
            "简体中文": "家用电器 (Home Appliances)",
            "English": "Home Appliances",
            "Nigerian Pidgin": "Home Appliances"
        },
        "五金与建材工具 (Hardware & Building Materials)": {
            "简体中文": "五金与建材工具 (Hardware & Building Materials)",
            "English": "Hardware & Building Materials",
            "Nigerian Pidgin": "Hardware & Building tools"
        },
        "Hardware & Building Materials": {
            "简体中文": "五金与建材工具 (Hardware & Building Materials)",
            "English": "Hardware & Building Materials",
            "Nigerian Pidgin": "Hardware & Building tools"
        },
        "Hardware & Building tools": {
            "简体中文": "五金与建材工具 (Hardware & Building Materials)",
            "English": "Hardware & Building Materials",
            "Nigerian Pidgin": "Hardware & Building tools"
        },
        "其他杂品清仓 (Other Clearing Items)": {
            "简体中文": "其他杂品清仓 (Other Clearing Items)",
            "English": "Other Clearance Items",
            "Nigerian Pidgin": "Other Clearance Cargo"
        },
        "Other Clearance Items": {
            "简体中文": "其他杂品清仓 (Other Clearing Items)",
            "English": "Other Clearance Items",
            "Nigerian Pidgin": "Other Clearance Cargo"
        },
        "Other Clearance Cargo": {
            "简体中文": "其他杂品清仓 (Other Clearing Items)",
            "English": "Other Clearance Items",
            "Nigerian Pidgin": "Other Clearance Cargo"
        },
        # Selling points
        "货到付款 (Cash on Delivery / COD)": {
            "简体中文": "货到付款 (Cash on Delivery / COD)",
            "English": "Cash on Delivery / COD",
            "Nigerian Pidgin": "Cash on Delivery (COD) allowed"
        },
        "Cash on Delivery / COD": {
            "简体中文": "货到付款 (Cash on Delivery / COD)",
            "English": "Cash on Delivery / COD",
            "Nigerian Pidgin": "Cash on Delivery (COD) allowed"
        },
        "Cash on Delivery (COD) allowed": {
            "简体中文": "货到付款 (Cash on Delivery / COD)",
            "English": "Cash on Delivery / COD",
            "Nigerian Pidgin": "Cash on Delivery (COD) allowed"
        },
        "拉各斯本土仓库现场看货/自提 (Lagos Warehouse Pick-up)": {
            "简体中文": "拉各斯本土仓库现场看货/自提 (Lagos Warehouse Pick-up)",
            "English": "Lagos Warehouse Self-Pickup",
            "Nigerian Pidgin": "Lagos warehouse pickup sharp-sharp"
        },
        "Lagos Warehouse Self-Pickup": {
            "简体中文": "拉各斯本土仓库现场看货/自提 (Lagos Warehouse Pick-up)",
            "English": "Lagos Warehouse Self-Pickup",
            "Nigerian Pidgin": "Lagos warehouse pickup sharp-sharp"
        },
        "Lagos warehouse pickup sharp-sharp": {
            "简体中文": "拉各斯本土仓库现场看货/自提 (Lagos Warehouse Pick-up)",
            "English": "Lagos Warehouse Self-Pickup",
            "Nigerian Pidgin": "Lagos warehouse pickup sharp-sharp"
        },
        "源头清仓超低价 (Direct Importer Wholesale Price)": {
            "简体中文": "源头清仓超低价 (Direct Importer Wholesale Price)",
            "English": "Direct Importer Price",
            "Nigerian Pidgin": "Direct Importer wholesale price"
        },
        "Direct Importer Price": {
            "简体中文": "源头清仓超低价 (Direct Importer Wholesale Price)",
            "English": "Direct Importer Price",
            "Nigerian Pidgin": "Direct Importer wholesale price"
        },
        "Direct Importer wholesale price": {
            "简体中文": "源头清仓超低价 (Direct Importer Wholesale Price)",
            "English": "Direct Importer Price",
            "Nigerian Pidgin": "Direct Importer wholesale price"
        },
        "集装箱刚刚到港 (Fresh Container Landing)": {
            "简体中文": "集装箱刚刚到港 (Fresh Container Landing)",
            "English": "Fresh Container Landing",
            "Nigerian Pidgin": "Container just land now-now"
        },
        "Fresh Container Landing": {
            "简体中文": "集装箱刚刚到港 (Fresh Container Landing)",
            "English": "Fresh Container Landing",
            "Nigerian Pidgin": "Container just land now-now"
        },
        "Container just land now-now": {
            "简体中文": "集装箱刚刚到港 (Fresh Container Landing)",
            "English": "Fresh Container Landing",
            "Nigerian Pidgin": "Container just land now-now"
        },
        "极致坚固耐用 (Heavy Duty & Super Durable)": {
            "简体中文": "极致坚固耐用 (Heavy Duty & Super Durable)",
            "English": "Super Durable / Heavy Duty",
            "Nigerian Pidgin": "Na double quality - solid scatter"
        },
        "Super Durable / Heavy Duty": {
            "简体中文": "极致坚固耐用 (Heavy Duty & Super Durable)",
            "English": "Super Durable / Heavy Duty",
            "Nigerian Pidgin": "Na double quality - solid scatter"
        },
        "Na double quality - solid scatter": {
            "简体中文": "极致坚固耐用 (Heavy Duty & Super Durable)",
            "English": "Super Durable / Heavy Duty",
            "Nigerian Pidgin": "Na double quality - solid scatter"
        },
        "库存告急先到先得 (Limited Stock, First Come First Served)": {
            "简体中文": "库存告急先到先得 (Limited Stock, First Come First Served)",
            "English": "Limited Stock / First Come First Served",
            "Nigerian Pidgin": "First come first serve - Stock dey clear"
        },
        "Limited Stock / First Come First Served": {
            "简体中文": "库存告急先到先得 (Limited Stock, First Come First Served)",
            "English": "Limited Stock / First Come First Served",
            "Nigerian Pidgin": "First come first serve - Stock dey clear"
        },
        "First come first serve - Stock dey clear": {
            "简体中文": "库存告急先到先得 (Limited Stock, First Come First Served)",
            "English": "Limited Stock / First Come First Served",
            "Nigerian Pidgin": "First come first serve - Stock dey clear"
        }
    }
    
    # Try finding exact lookup
    if text_clean in dict_map:
        return dict_map[text_clean].get(target_lang, text)
        
    # Try case-insensitive lookup
    for key, val_dict in dict_map.items():
        if text_clean.lower() == key.lower() or text_clean.lower() in [v.lower() for v in val_dict.values()]:
            return val_dict.get(target_lang, text)
            
    # If not found in dict, and API is available, use LLM
    if openai_api_key:
        system_prompt = f"You are a professional B2B platform translator. Translate this category name or key selling point from {sys_lang} to {target_lang}. Return ONLY the direct translation, nothing else. No quotes, no explanations, no prefix. Clean translation only."
        user_prompt = text_clean
        try:
            val = _call_openai(system_prompt, user_prompt, temperature=0.3).strip()
            if val:
                return val
        except Exception:
            pass
    # Free Google Translate API fallback (requires internet)
    import urllib.request
    import urllib.parse
    import json
    
    lang_map = {
        "简体中文": "zh-CN",
        "English": "en",
        "Nigerian Pidgin": "en"  # Fallback to English for Pidgin in Google Translate
    }
    
    sl = "auto"
    tl = lang_map.get(target_lang, "en")
    
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + sl + "&tl=" + tl + "&dt=t&q=" + urllib.parse.quote(text_clean)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode('utf-8'))
            val = res[0][0][0]
            if val:
                return val
    except Exception:
        pass
            
    return text_clean

def get_mock_marketing_copy(prod_name, prod_category, price, moq, sell_points, extra_info, phone, use_pidgin):
    points_str = "\n".join([f"- {pt}" for pt in sell_points])
    pidgin_note = "Aje o! " if use_pidgin else ""
    return f"""
#### 💥 紧急抛售风 (Urgent Clearance - High Scarcity)
🔥 **LAGOS CONTAINER LIQUIDATION! EVERYTHING MUST GO!** 🔥

{pidgin_note}We are clearing out a fresh container load of **{prod_name}** ({prod_category}) direct from the port! No stories, no middleman price!

- 📍 **Lagos Warehouse Self-Pickup**: Plot 12, Osolo Way, Ajao Estate, Ikeja, Lagos
- 💰 **Chop Life Price**: **{price:,} NGN** per unit! (Market price is over {int(price*1.4):,} NGN!)
- 📦 **Strict MOQ (Wholesale only)**: **{moq} units**
- ⚡ **Features**:
{points_str}
- 🚨 **Scarcity**: {extra_info} First come, first served!

📞 **WhatsApp us now to lock your batch**: {phone}

---

#### 💎 代理招商商机风 (Reseller Portal - B2B Wholesaler)
💼 **ATTENTION ALL LAGOS TRADERS & RESELLERS!** 💼

Looking for the best wholesale profit margin in Nigeria? {pidgin_note}This is direct container clearance of high-quality **{prod_name}**. Buy direct from the importer and double your profit!

- 💵 **Wholesale Price**: **{price:,} NGN** per piece
- 📦 **Minimum Order**: {moq} units (Collect from Ajao Estate warehouse)
- 🤝 **Payment Safe**: Cash on Delivery (COD) allowed for self-pickup. Verify the goods before paying.
- ✨ **Key Highlights**:
{points_str}

📞 **WhatsApp our wholesale manager**: {phone}

---

#### 📱 快捷直销风 (WhatsApp status / Jiji post quick snippet)
💥 **Direct Container clearance - {prod_name}** 💥
{pidgin_note}Na double quality! Correct imported standard!
👇👇👇
- 💰 Price: **{price:,} NGN** (Strict Wholesale)
- 📦 MOQ: **{moq} units**
- 📍 Location: Lagos warehouse pickup (Osolo Way)
- 📞 WhatsApp status orders: {phone}
- ⚡ {extra_info}
NO DEPOSIT SCAMS! Pay in warehouse after inspection!
"""

def get_mock_video_script(ch_script, active_prod, price, phone, address):
    return f"""
| Section (板块) | Visual & Camera (画面与镜头) | Dialogue / Audio (旁白与台词) | Action & Tone (动作与语气) |
| :--- | :--- | :--- | :--- |
| **Hook (0-3s)** | Camera close-up on the host jumping onto the {active_prod}. Camera shakes to show impact. | "Aje! Look at this quality! I am 90kg and this {active_prod} is not even bending at all!" | Host jumps heavily on the product, looking directly into the lens. Energetic and loud tone. |
| **Body (4-15s)** | Pan to show stacks of {active_prod} inside the Lagos warehouse. Show container doors open. | "No story, container just land Lagos today! We are clearing everything direct from importer!" | Host gestures to the container load, showing the scale of the stock. Exciting tone. |
| **Offer (16-25s)** | Close-up on the price tag and WhatsApp phone number on the screen. | "Don't pay market retail price! Buy wholesale for only **{price:,} NGN**! MOQ is 50." | Host shows the price on a placard or phone screen, pointing at it. |
| **CTA (26-30s)** | Zoom into host holding a green WhatsApp icon card. | "We are at Osolo Way, Ikeja. Click WhatsApp below or call {phone} to secure your batch now before it clears!" | Host points down at the WhatsApp button, smiling. Urgent and friendly tone. |
"""

def get_mock_video_script_by_id(idx, sys_lang):
    active_prod = st.session_state.get("active_prod", "Heavy Duty Plastic Stackable Chair")
    price = st.session_state.get("active_price", 12500)
    phone = st.session_state.get("t2_phone_in", "+86 15521176830")
    address = st.session_state.get("lagos_address", "Lagos warehouse")
    
    if idx == 0:
        return f"""
| Section (板块) | Visual & Camera (画面与镜头) | Dialogue / Audio (旁白与台词) | Action & Tone (动作与语气) |
| :--- | :--- | :--- | :--- |
| **Hook (0-3s)** | Camera close-up on the host jumping onto the {active_prod}. Camera shakes to show impact. | "Aje! Look at this quality! I am 90kg and this {active_prod} is not even bending at all!" | Host jumps heavily on the product, looking directly into the lens. Energetic and loud tone. |
| **Body (4-15s)** | Pan to show stacks of {active_prod} inside the Lagos warehouse. Show container doors open. | "No story, container just land Lagos today! We are clearing everything direct from importer!" | Host gestures to the container load, showing the scale of the stock. Exciting tone. |
| **Offer (16-25s)** | Close-up on the price tag and WhatsApp phone number on the screen. | "Don't pay market retail price! Buy wholesale for only **{price:,} NGN**! MOQ is 50." | Host shows the price on a placard or phone screen, pointing at it. |
| **CTA (26-30s)** | Zoom into host holding a green WhatsApp icon card. | "We are at Osolo Way, Ikeja. Click WhatsApp below or call {phone} to secure your batch now before it clears!" | Host points down at the WhatsApp button, smiling. Urgent and friendly tone. |
"""
    elif idx == 1:
        return f"""
| Section (板块) | Visual & Camera (画面与镜头) | Dialogue / Audio (旁白与台词) | Action & Tone (动作与语气) |
| :--- | :--- | :--- | :--- |
| **Hook (0-3s)** | Host rolls a heavy container tire directly towards the camera, pretending to run over the lens. | "Oya look here! Direct wholesale clearance tire just land Lagos warehouse!" | Host rolls the tire with a high energy expression. Loud and engaging voice. |
| **Body (4-15s)** | Close-up on the deep tread patterns of the tire. Show the warehouse worker pointing to the steel wiring. | "Na double wire quality! Not like those cheap copy-copy in the open market. This one go last you for years!" | Worker points to tire details, smiling confidently. |
| **Offer (16-25s)** | Camera shows wholesale pricing sticker on tire: **{price:,} NGN**. | "Buy direct from importer at container wholesale price. Only **{price:,} NGN** per piece. Strictly for traders." | Host highlights pricing placard next to tires. |
| **CTA (26-30s)** | Host walks to warehouse gate, pointing at the office sign. | "We dey Lagos. WhatsApp {phone} to place your order now. Payment on pickup is 100% allowed!" | Host waves directly to the camera, inviting them to WhatsApp. |
"""
    else:
        return f"""
| Section (板块) | Visual & Camera (画面与镜头) | Dialogue / Audio (旁白与台词) | Action & Tone (动作与语气) |
| :--- | :--- | :--- | :--- |
| **Hook (0-3s)** | Host hits the product container with a heavy metal wrench to test durability. Spark sparks. | "na real iron quality, no stories! We test am live for warehouse!" | Host strikes the product confidently with a hammer/wrench. Shocking hook. |
| **Body (4-15s)** | Close-up on the product surface showing zero scratches or damage. Workers carry batches in background. | "Imported direct from source. If you sell this one, your customer go thank you for life. High profit margin!" | Workers demonstrate lifting and placing, showing robust structure. |
| **Offer (16-25s)** | Show a package listing the MOQ and wholesale pricing list. | "Whole container liquidation price: **{price:,} NGN**! Strictly minimum of {st.session_state.get('active_moq', 50)} units." | Host points at the packaging boxes. |
| **CTA (26-30s)** | Host points down at the green WhatsApp link overlay. | "Click WhatsApp below now to secure your cargo gate pass. Limited warehouse space left!" | Host points down, urgent and authoritative B2B wholesale tone. |
"""

def get_mock_ad_campaign_guide(active_prod, prod_category, price, moq, phone):
    return f"""
#### 🎯 受众定向配置 (Audience Targeting Plan)

| Parameter (参数) | Configuration Details (配置明细) | Rationale (逻辑定向原因) |
| :--- | :--- | :--- |
| **Geographic (地域)** | Lagos State, Nigeria (拉各斯州) | Focus budget where 70% of B2B buyers reside. |
| **Age & Gender (年龄/性别)** | 25 - 55, All Genders | Targets business owners and resellers. |
| **Detailed Targeting (兴趣词)** | **Reseller, Wholesale, Retail, Importer, Jiji.ng** | Reaches local traders and active merchants. |
| **Behavior (行为限制)** | **Engaged Shoppers (互动买家)** | Filters out users who do not click CTA buttons. |
| **Ad Placement (版位)** | Meta Advantage+ Placement (自动版位) | Maximizes cost-efficiency across FB/IG. |

---

#### ✍️ A/B 测试广告文案 (Ad Copy Variations)

##### 🅰️ Variation A: Hook on Wholesale Profit (利润痛点风)
> **Headline**: Double Your Retail Profit in Lagos! 🇳🇬
> 
> **Primary Text**: Direct Container Clearance! Importer price for **{active_prod}** now selling at only **{price:,} NGN**. Perfect wholesale deal for traders and retailers. Pick up directly at our Lagos warehouse. Low MOQ of {moq} units. Click to chat with us on WhatsApp now! 📞

##### 🅱️ Variation B: Hook on Durability (质量坚固风)
> **Headline**: Heavy Duty {active_prod} - Na Double Quality! 💥
> 
> **Primary Text**: Tired of cheap materials that break? Our imported **{active_prod}** is super strong and durable (Aje o!). Direct clearance deal. Pay on delivery at warehouse. WhatsApp us at {phone} to lock your orders!

---

#### 📊 广告指标诊断与调优 (Tuning & Diagnosis Guide)

- **Low CTR (点击率 < 1.5%)**:
  - *Diagnosis*: Creative is too polished or look like retail ads.
  - *Fix*: Replace with raw video showing stress-testing or warehouse container unloading.
- **High Click, Low WhatsApp Lead (加粉率 < 15%)**:
  - *Diagnosis*: Buyer did not expect wholesale MOQ.
  - *Fix*: Write the MOQ (**{moq} units**) and price (**{price:,} NGN**) clearly in the ad headline.
"""

def process_warehouse_image_advanced(uploaded_file, phone, apply_wm, wm_position, wm_color, wm_scale, template_type="No Template", price=12500, moq=50, apply_qr=False, removebg_method="u2net"):
    try:
        # Open uploaded image
        image = Image.open(uploaded_file).convert("RGBA")
        
        # Background removal process
        if "关闭去背景" in removebg_method or "None" in removebg_method or "Skip" in removebg_method or "No clean background" in removebg_method:
            # Skip background removal, keep original image (convert to RGBA to match other paths)
            pass
        elif "腾讯云数据万象" in removebg_method or "Tencent Cloud CI" in removebg_method:
            # Call Tencent Cloud CI (Data Infinite)
            try:
                # Retrieve keys from st.secrets (fallback to session state)
                appid = tencent_appid if tencent_appid else st.session_state.get("tencent_appid", "")
                secret_id = tencent_secret_id if tencent_secret_id else st.session_state.get("tencent_secret_id", "")
                secret_key = (tencent_secret_key if tencent_secret_key else st.session_state.get("tencent_secret_key", "")).strip()
                bucket = (tencent_bucket if tencent_bucket else st.session_state.get("tencent_bucket", "")).strip()
                region = (tencent_region if tencent_region else st.session_state.get("tencent_region", "ap-guangzhou")).strip()
                
                # Check for required fields
                if not secret_key or not bucket:
                    raise ValueError("Tencent SecretKey and COS Bucket Name must be configured in the sidebar!")
                
                # Dynamic imports to prevent startup issues
                from qcloud_cos import CosConfig
                from qcloud_cos import CosS3Client
                import uuid
                import requests
                
                # Standardize bucket name format
                bucket_name = bucket
                if appid and not bucket_name.endswith(f"-{appid}"):
                    bucket_name = f"{bucket_name}-{appid}"
                
                # Setup client
                config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
                client = CosS3Client(config)
                
                # Read original image bytes
                uploaded_file.seek(0)
                body_data = uploaded_file.read()
                
                # Generate a safe temp key in COS
                temp_key = f"temp_matting_{uuid.uuid4().hex}.png"
                
                # Determine which CI process to call
                ci_process = "AIPicMatting"
                if "GoodsMatting" in removebg_method or "商品抠图" in removebg_method:
                    ci_process = "GoodsMatting"
                
                # Upload to COS
                client.put_object(
                    Bucket=bucket_name,
                    Body=body_data,
                    Key=temp_key
                )
                
                try:
                    # Get signed URL with CI download-time processing param
                    url = client.get_presigned_download_url(
                        Bucket=bucket_name,
                        Key=temp_key,
                        Params={'ci-process': ci_process}
                    )
                    
                    # Fetch from Data Infinite
                    res = requests.get(url)
                    if res.status_code == 200:
                        no_bg_image = Image.open(io.BytesIO(res.content)).convert("RGBA")
                        white_bg = Image.new("RGBA", no_bg_image.size, (255, 255, 255, 255))
                        image = Image.alpha_composite(white_bg, no_bg_image)
                    else:
                        raise Exception(f"HTTP Status {res.status_code}: {res.text}")
                finally:
                    # Clean up temporary COS object
                    try:
                        client.delete_object(Bucket=bucket_name, Key=temp_key)
                    except Exception:
                        pass
            except Exception as tencent_err:
                st.error(f"Tencent Cloud CI failed: {tencent_err}")
                st.warning("Falling back to local background removal or brightening.")
                # Fallback to local rembg if available, otherwise brighten
                if REMBG_AVAILABLE:
                    try:
                        model_name = "u2net"
                        if "isnet" in removebg_method:
                            model_name = "isnet-general-use"
                        
                        from rembg import new_session
                        session = new_session(model_name)
                        no_bg_image = remove(image, session=session)
                        
                        white_bg = Image.new("RGBA", no_bg_image.size, (255, 255, 255, 255))
                        image = Image.alpha_composite(white_bg, no_bg_image)
                    except Exception as local_err:
                        st.warning(f"Local background removal fallback failed: {local_err}. Brightening image instead.")
                        enhancer = ImageEnhance.Brightness(image)
                        image = enhancer.enhance(1.1)
                else:
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(1.1)
        else:
            # Local rembg with selected model (isnet-general-use or u2net)
            if REMBG_AVAILABLE:
                try:
                    model_name = "u2net"
                    if "isnet" in removebg_method:
                        model_name = "isnet-general-use"
                    
                    from rembg import new_session
                    session = new_session(model_name)
                    no_bg_image = remove(image, session=session)
                    
                    white_bg = Image.new("RGBA", no_bg_image.size, (255, 255, 255, 255))
                    image = Image.alpha_composite(white_bg, no_bg_image)
                except Exception as local_err:
                    st.warning(f"Local background removal failed: {local_err}. Brightening image instead.")
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(1.1)
            else:
                # Fallback when rembg is not imported
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.1)

            
        # Determine if banner is active
        has_banner = template_type and ("Clearance Banner" in template_type or "清仓大图海报横幅" in template_type or "Down Wholesale Clearance Banner" in template_type)
            
        # 1. Apply B2B Templates
        if template_type and template_type not in ["No Template", "No Template (Watermark Only)", "No Template (Watermark only)", "无排版模板 (仅去噪与水印)"]:
            image = image.convert("RGBA")
            w, h = image.size
            
            if has_banner:
                # Solid overlay block at the bottom
                banner_h = int(h * 0.16)
                overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)
                
                # Draw dark background block (semi-transparent for lighter appearance)
                draw.rectangle([0, h - banner_h, w, h], fill=(6, 9, 19, 120))
                
                # Draw top neon border line on the banner
                draw.line([0, h - banner_h, w, h - banner_h], fill=(0, 242, 254, 255), width=max(2, int(h * 0.006)))
                
                title_font_size = max(12, int(banner_h * 0.28))
                info_font_size = max(10, int(banner_h * 0.22))
                
                try:
                    title_font = ImageFont.truetype("arial.ttf", title_font_size)
                    info_font = ImageFont.truetype("arial.ttf", info_font_size)
                except IOError:
                    title_font = ImageFont.load_default()
                    info_font = ImageFont.load_default()
                    
                title_text = "NIGERIA WAREHOUSE DIRECT CLEARANCE"
                details_text = f"PRICE: {price:,} NGN | MOQ: {moq} PCS | WhatsApp: {phone}"
                
                # Dynamic font scaling to prevent truncation
                max_text_width = w - int(w * 0.1)  # 90% of image width
                if apply_qr:
                    # If QR code is drawn inside the banner, reserve space on the right
                    qr_w_calc = int(banner_h * 0.8)
                    max_text_width = w - qr_w_calc - int(w * 0.08)
                
                # Scale down title font size until it fits
                while title_font_size > 8:
                    try:
                        bbox = draw.textbbox((0, 0), title_text, font=title_font)
                        tw = bbox[2] - bbox[0]
                    except AttributeError:
                        tw, _ = draw.textsize(title_text, font=title_font)
                    if tw <= max_text_width:
                        break
                    title_font_size -= 1
                    try:
                        title_font = ImageFont.truetype("arial.ttf", title_font_size)
                    except IOError:
                        title_font = ImageFont.load_default()

                # Scale down details font size until it fits
                while info_font_size > 8:
                    try:
                        bbox = draw.textbbox((0, 0), details_text, font=info_font)
                        tw = bbox[2] - bbox[0]
                    except AttributeError:
                        tw, _ = draw.textsize(details_text, font=info_font)
                    if tw <= max_text_width:
                        break
                    info_font_size -= 1
                    try:
                        info_font = ImageFont.truetype("arial.ttf", info_font_size)
                    except IOError:
                        info_font = ImageFont.load_default()
                
                draw.text((int(w * 0.05), h - int(banner_h * 0.72)), title_text, fill=(255, 255, 255, 255), font=title_font)
                draw.text((int(w * 0.05), h - int(banner_h * 0.38)), details_text, fill=(0, 242, 254, 255), font=info_font)
                
                image = Image.alpha_composite(image, overlay)
                
            elif "Paid Stamp" in template_type or "付款核对红色印章" in template_type or "Sterling Bank Paid Stamp" in template_type or "Zenith Bank Paid Stamp" in template_type:
                stamp_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(stamp_overlay)
                
                stamp_size = int(min(w, h) * 0.22)
                if apply_qr:
                    # Shift stamp to bottom-left to avoid conflict with QR code in bottom-right
                    cx = int(stamp_size * 0.7) + int(w * 0.05)
                else:
                    cx = w - int(stamp_size * 0.7) - int(w * 0.05)
                cy = h - int(stamp_size * 0.7) - int(h * 0.05)
                r = stamp_size // 2
                
                # Draw red double outline
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 38, 38, 220), width=max(2, int(stamp_size * 0.04)))
                draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=(220, 38, 38, 160), width=1)
                
                font_size = max(8, int(stamp_size * 0.13))
                try:
                    stamp_font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    stamp_font = ImageFont.load_default()
                    
                # Try to extract bank name dynamically from account_number input
                bank_name_drawn = "STERLING BANK"
                try:
                    act_num = globals().get("account_number", "")
                    if " - " in act_num:
                        raw_bank = act_num.split(" - ")[-1].strip().upper()
                        for suffix in ["PLC", "LIMITED", "LTD", "BANK"]:
                            if suffix in raw_bank:
                                raw_bank = raw_bank.replace(suffix, "").strip()
                        if raw_bank:
                            bank_name_drawn = f"{raw_bank} BANK"
                except Exception:
                    pass
                
                # Center the text based on its length
                offset_ratio = 0.75
                if len(bank_name_drawn) > 12:
                    offset_ratio = 0.85
                elif len(bank_name_drawn) < 8:
                    offset_ratio = 0.65
                
                draw.text((cx - int(r * offset_ratio), cy - int(r*0.4)), bank_name_drawn, fill=(220, 38, 38, 220), font=stamp_font)
                draw.text((cx - int(r*0.65), cy - int(r*0.05)), "PAID & VERIFIED", fill=(220, 38, 38, 220), font=stamp_font)
                draw.text((cx - int(r*0.75), cy + int(r*0.3)), "RELEASE CARGO", fill=(220, 38, 38, 220), font=stamp_font)
                
                image = Image.alpha_composite(image, stamp_overlay)

        # 2. Apply Text Watermark (Skip if Clearance Banner is active, to avoid double text watermark info)
        if apply_wm and phone and not has_banner:
            image = image.convert("RGBA")
            # Create a transparent overlay for the watermark
            txt_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(txt_overlay)
            w, h = image.size
            
            # Map colors
            color_map = {
                "极光紫 (Violet)": (124, 58, 237),
                "深海蓝 (Blue)": (37, 99, 235),
                "警示红 (Red)": (220, 38, 38),
                "碳灰色 (Charcoal)": (75, 85, 99),
                "Violet light": (124, 58, 237),
                "Blue ocean": (37, 99, 235),
                "Red alert": (220, 38, 38),
                "Charcoal dark": (75, 85, 99),
                "Violet": (124, 58, 237),
                "Blue": (37, 99, 235),
                "Red": (220, 38, 38),
                "Charcoal": (75, 85, 99)
            }
            accent_color = color_map.get(wm_color, (124, 58, 237))
            
            # Determine font size based on scale
            font_size = int(h * (wm_scale / 100.0))
            if font_size < 12:
                font_size = 12
                
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
                
            wm_text = f"WhatsApp: {phone}"
            
            # Calculate text size using textbbox
            try:
                bbox = draw.textbbox((0, 0), wm_text, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            except AttributeError:
                tw, th = draw.textsize(wm_text, font=font)
                
            pad_x, pad_y = int(font_size * 0.6), int(font_size * 0.3)
            cap_w, cap_h = tw + 2 * pad_x, th + 2 * pad_y
            
            # Grid overlay fallback if "Tile" or "平铺" is chosen
            if "Tile" in wm_position or "平铺" in wm_position:
                for y_grid in range(int(h*0.1), h, int(h*0.3)):
                    for x_grid in range(int(w*0.1), w, int(w*0.4)):
                        draw.text((x_grid, y_grid), wm_text, fill=accent_color + (80,), font=font)
            else:
                # Determine position coordinates
                pos_x, pos_y = 0, 0
                if "Right" in wm_position or "右" in wm_position:
                    pos_x = w - cap_w - int(w * 0.05)
                elif "Left" in wm_position or "左" in wm_position:
                    pos_x = int(w * 0.05)
                elif "Center" in wm_position or "中" in wm_position:
                    pos_x = (w - cap_w) // 2
                else:
                    pos_x = w - cap_w - int(w * 0.05)
                    
                if "Bottom" in wm_position or "下" in wm_position:
                    pos_y = h - cap_h - int(h * 0.05)
                elif "Top" in wm_position or "上" in wm_position:
                    pos_y = int(h * 0.05)
                elif "Center" in wm_position or "中" in wm_position:
                    pos_y = (h - cap_h) // 2
                else:
                    pos_y = h - cap_h - int(h * 0.05)
                
                # Draw elegant capsule shape (semi-transparent for lighter appearance)
                draw.rounded_rectangle(
                    [pos_x, pos_y, pos_x + cap_w, pos_y + cap_h],
                    radius=int(font_size * 0.3),
                    fill=(11, 15, 25, 120),
                    outline=accent_color + (255,),
                    width=2
                )
                # Draw text on overlay
                draw.text((pos_x + pad_x, pos_y + pad_y), wm_text, fill=(255, 255, 255, 255), font=font)
            
            # Composite overlay
            image = Image.alpha_composite(image, txt_overlay)
            
        # 3. Apply WhatsApp QR Code Watermark
        if apply_qr:
            qr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_qrcode.png")
            if os.path.exists(qr_path):
                try:
                    qr_img = Image.open(qr_path).convert("RGBA")
                    w, h = image.size
                    
                    if has_banner:
                        banner_h = int(h * 0.16)
                        # Make QR code 80% of banner height
                        qr_w = int(banner_h * 0.8)
                        pos_x = w - qr_w - int(banner_h * 0.15)
                        pos_y = h - banner_h + (banner_h - qr_w) // 2
                    else:
                        # Calculate QR code size (e.g. 16% of the min dimension, min 80px)
                        qr_w = int(min(w, h) * 0.16)
                        if qr_w < 80:
                            qr_w = 80
                        margin_x = int(w * 0.05)
                        margin_y = int(h * 0.05)
                        
                        # Determine QR position (stacked above the text watermark if both are in Bottom-Right or Bottom-Left)
                        pos_x = w - qr_w - margin_x
                        pos_y = h - qr_w - margin_y
                        
                        if apply_wm and phone and ("Tile" not in wm_position and "平铺" not in wm_position):
                            font_size_calc = int(h * (wm_scale / 100.0))
                            if font_size_calc < 12:
                                font_size_calc = 12
                            cap_h_calc = int(font_size_calc * 1.6)
                            
                            if ("Bottom" in wm_position or "下" in wm_position) and ("Right" in wm_position or "右" in wm_position):
                                pos_y = h - qr_w - cap_h_calc - margin_y - int(h * 0.02)
                            elif ("Bottom" in wm_position or "下" in wm_position) and ("Left" in wm_position or "左" in wm_position):
                                pos_x = margin_x
                                pos_y = h - qr_w - cap_h_calc - margin_y - int(h * 0.02)
                    
                    qr_img = qr_img.resize((qr_w, qr_w), Image.Resampling.LANCZOS)
                    qr_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
                    qr_overlay.paste(qr_img, (pos_x, pos_y))
                    image = Image.alpha_composite(image, qr_overlay)
                except Exception as qr_err:
                    st.warning(f"Failed to apply QR Code: {qr_err}")
            
        return image.convert("RGB")
    except Exception as e:
        st.error(f"Image processing error: {e}")
        return None

def render_fb_ad_mockup(text, img_b64, phone):
    media_html = ""
    if img_b64:
        media_html = f'<div class="fb-ad-media"><img src="{img_b64}"/></div>'
    else:
        media_html = '<div class="fb-ad-media" style="padding: 40px; color: #888; background: #242526; height: 180px;"><div style="margin: auto;"><i class="fa-solid fa-image" style="font-size: 2.5rem; margin-bottom: 10px;"></i><br/>No Image Uploaded</div></div>'
        
    html = f"""
    <div class="fb-ad-container">
        <div class="fb-ad-header">
            <div class="fb-ad-avatar">🇳🇬</div>
            <div class="fb-ad-header-text">
                <div class="fb-ad-name">Lagos Wholesale Clearance Importers</div>
                <div class="fb-ad-meta">Sponsored · <i class="fa-solid fa-earth-africa"></i></div>
            </div>
        </div>
        <div class="fb-ad-text">{text}</div>
        {media_html}
        <div class="fb-ad-footer-bar">
            <div class="fb-ad-footer-left">
                <div class="fb-ad-caption">LAGOS WAREHOUSE</div>
                <div class="fb-ad-headline">Direct Importer Container Clearance Deals!</div>
            </div>
            <a class="fb-ad-btn" href="https://wa.me/{phone.replace(' ', '').replace('+', '')}" target="_blank">WhatsApp</a>
        </div>
    </div>
    """
    return html

def render_wa_chat_mockup(user_text, bot_text):
    html = f"""
    <div class="whatsapp-container">
        <div class="whatsapp-header">
            <div class="whatsapp-avatar"><i class="fa-brands fa-whatsapp"></i></div>
            <div class="whatsapp-header-info">
                <div class="whatsapp-header-name">Lagos Clearance Assistant</div>
                <div class="whatsapp-header-status">Online</div>
            </div>
        </div>
        <div class="whatsapp-body">
            <div class="whatsapp-msg whatsapp-msg-in">
                {user_text}
            </div>
            <div class="whatsapp-msg whatsapp-msg-out">
                {bot_text}
            </div>
        </div>
    </div>
    """
    return html

# ---------------------------------------------------------
# Inject custom styles & Define main navigation tabs
# ---------------------------------------------------------
inject_custom_css()

def render_dashboard_header(title, subtitle, badge):
    # Remove leading emojis from title if present
    clean_title = title.split(maxsplit=1)[1] if title.startswith(('📢', '🖼️', '💬', '🎬', '📈', '📚')) else title
    st.markdown(f"""
    <div class="dashboard-header" style="margin-bottom: 2rem; border-bottom: 1px solid rgba(0, 242, 254, 0.1); padding-bottom: 1.5rem;">
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <span style="font-family: 'Outfit', sans-serif; font-size: 0.75rem; font-weight: 600; color: #00F2FE; letter-spacing: 2px; text-transform: uppercase;">{badge}</span>
            <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin: 0; display: flex; align-items: center; gap: 12px; line-height: 1.2;">{clean_title}</h2>
            <p style="font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #94a3b8; margin: 6px 0 0 0; line-height: 1.6; max-width: 900px;">{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Define navigation functions
def render_navbar():
    st.markdown('<div class="navbar-wrapper">', unsafe_allow_html=True)
    cols = st.columns([1.8, 1, 1, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown('<div class="nav-logo"><i class="fa-solid fa-bolt" style="color:#00F2FE;"></i> Angel AI</div>', unsafe_allow_html=True)
        
    pages_list = [
        ("home", "🏠 " + ("首页" if sys_lang == "简体中文" else "Home" if sys_lang == "English" else "Home")),
        ("copy", "📢 " + ("文案" if sys_lang == "简体中文" else "Copy" if sys_lang == "English" else "Copy")),
        ("image", "🖼️ " + ("图片" if sys_lang == "简体中文" else "Image" if sys_lang == "English" else "Image")),
        ("sop", "💬 " + ("话术" if sys_lang == "简体中文" else "SOPs" if sys_lang == "English" else "SOPs")),
        ("video", "🎬 " + ("分析" if sys_lang == "简体中文" else "Analyze" if sys_lang == "English" else "Analyze")),
        ("ads", "📈 " + ("投流" if sys_lang == "简体中文" else "Ads" if sys_lang == "English" else "Ads")),
        ("training", "📚 " + ("教材" if sys_lang == "简体中文" else "Manual" if sys_lang == "English" else "Manual"))
    ]
    
    for i, (page_key, page_label) in enumerate(pages_list):
        with cols[i + 1]:
            if st.button(page_label, key=f"nav_btn_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Inject dynamic active tab styles
    active_key = st.session_state.current_page
    st.markdown(f"""
    <style>
        div[data-testid="stBaseButton-nav_btn_{active_key}"] button {{
            background: linear-gradient(90deg, rgba(0, 242, 254, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--accent-cyan) !important;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
            font-weight: 600 !important;
            transform: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def render_homepage():
    # Top status bar
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem; padding: 0.5rem 0;">
        <div style="font-family:'Outfit',sans-serif; font-size:1.5rem; font-weight:800; color:#FFFFFF; letter-spacing:1px; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-bolt" style="color:#00F2FE;"></i> Angel AI
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <span class="stBadge" style="background-color:rgba(0, 242, 254, 0.1); color:#00F2FE; border:1px solid rgba(0, 242, 254, 0.2); padding:4px 12px; border-radius:20px; font-size:0.8rem; font-family:'Outfit',sans-serif; font-weight:600;">
                <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background-color:#00F2FE; margin-right:6px; box-shadow:0 0 6px #00F2FE;"></span>
                SYSTEM ACTIVE
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-grid-overlay"></div>
        <div class="hero-badge">
            <span class="dot"></span> • DESIGN VAULT / 2026
        </div>
        <h1 class="hero-title">A launchpad for<br><span class="gradient-text">cinematic clearance interfaces.</span></h1>
        <p class="hero-subtitle">{L['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Clean leading emojis from titles
    clean_titles = {
        "copy": L['tab_copy'].split(maxsplit=1)[1] if L['tab_copy'].startswith("📢") else L['tab_copy'],
        "image": L['tab_image'].split(maxsplit=1)[1] if L['tab_image'].startswith("🖼️") else L['tab_image'],
        "sop": L['tab_sop'].split(maxsplit=1)[1] if L['tab_sop'].startswith("💬") else L['tab_sop'],
        "video": L['tab_video'].split(maxsplit=1)[1] if L['tab_video'].startswith("🎬") else L['tab_video'],
        "ads": L['tab_ads'].split(maxsplit=1)[1] if L['tab_ads'].startswith("📈") else L['tab_ads'],
        "training": L['tab_training'].split(maxsplit=1)[1] if L['tab_training'].startswith("📚") else L['tab_training'],
    }

    # Determine description translations
    if sys_lang == "简体中文":
        descs = {
            "copy": "西非爆款文案生成器。输入清仓商品品类与卖点，一键生成紧急清仓、代理招商、社媒状态等3套针对性英文/皮钦语文案。",
            "image": "仓储图片一键抠图洗白。快速擦除暗沉杂乱背景，替换为亮白商品底图，叠加客服防盗水印，防伪防走单。",
            "sop": "本地客服高频场景话术库。自动关联电话、自提仓地址、企业收款账号等配置信息，极速复制，防诈对账。",
            "video": "国内爆款短视频文案重构。将承重测试、源头工厂等分镜脚本完美重构为符合本地黑人演员实拍风格的配音与分镜。",
            "ads": "Meta & TikTok 投流辅助面板。配置测试预算、定向受众兴趣词与 A/B 测试素材，并提供转化率诊断指南。",
            "training": "本土仓标准化运营电子手册。出海团队、客服经理及仓管防骗对账实操指南，多语言对照，降低收汇风险。"
        }
        btn_label = "进入控制台 / Enter Console →"
    elif sys_lang == "English":
        descs = {
            "copy": "West African high-converting copywriter. Input category and key selling points to generate 3 tailored bulk/reseller clearance copies.",
            "image": "One-click background remover and watermark applicator. Turn raw warehouse photos into clean retail white-background assets.",
            "sop": "Standard WhatsApp customer negotiation scripts. Automatically links phone, warehouse address, and bank accounts.",
            "video": "Chinese viral video transcript localizer. Rebuilds weight tests and factory source scripts into local Nigerian camera shots and speech.",
            "ads": "Meta and TikTok targeting helper. Recommend budgets, interests, and A/B copies with diagnostic advice for Lagos market.",
            "training": "Nigeria clearance SOP handbook. Covers traffic generation, group building, bank transfer fake receipt checks and COD riders safety."
        }
        btn_label = "Enter Console →"
    else: # Pidgin
        descs = {
            "copy": "AI go write 3 correct styles of pure English and Pidgin clearance copies that go make buyers pay sharp-sharp.",
            "image": "Remove dark, dirty backgrounds from warehouse pictures, make them clean white, and slap watermark phone capsule.",
            "sop": "WhatsApp shortcuts for customer service to reply buyers fast. System go replace phone and bank info automatically.",
            "video": "Translate Chinese viral script to high energy Pidgin English shooting script with video camera details.",
            "ads": "Get targeted interest words for Nigeria, ad copy varieties, and performance guide for Lagos market.",
            "training": "Learn how to get traffic, build WhatsApp groups, avoid fake bank transfer receipt alert scams, and secure Lagos COD."
        }
        btn_label = "Enter Console Sharp-Sharp →"

    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown(f'''
            <div class="card-badge">📢 COPYWRITING</div>
            <div class="card-subtitle-sub">/text-to-copy</div>
            <div class="card-title-main">{clean_titles['copy']}</div>
            <p class="card-desc-text">{descs['copy']}</p>
            ''', unsafe_allow_html=True)
            if st.button(btn_label, key="enter_copy", use_container_width=True, type="primary"):
                st.session_state.current_page = "copy"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown(f'''
            <div class="card-badge">🖼️ IMAGE CLEAN</div>
            <div class="card-subtitle-sub">/image-clean</div>
            <div class="card-title-main">{clean_titles['image']}</div>
            <p class="card-desc-text">{descs['image']}</p>
            ''', unsafe_allow_html=True)
            if st.button(btn_label, key="enter_image", use_container_width=True, type="primary"):
                st.session_state.current_page = "image"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.markdown(f'''
            <div class="card-badge">💬 SOP HUB</div>
            <div class="card-subtitle-sub">/whatsapp-sop</div>
            <div class="card-title-main">{clean_titles['sop']}</div>
            <p class="card-desc-text">{descs['sop']}</p>
            ''', unsafe_allow_html=True)
            if st.button(btn_label, key="enter_sop", use_container_width=True, type="primary"):
                st.session_state.current_page = "sop"
                st.rerun()

    col4, col5, col6 = st.columns(3)
    
    with col4:
        with st.container(border=True):
            st.markdown(f'''
            <div class="card-badge">🎬 VIDEO REBUILDER</div>
            <div class="card-subtitle-sub">/video-local-script</div>
            <div class="card-title-main">{clean_titles['video']}</div>
            <p class="card-desc-text">{descs['video']}</p>
            ''', unsafe_allow_html=True)
            if st.button(btn_label, key="enter_video", use_container_width=True, type="primary"):
                st.session_state.current_page = "video"
                st.rerun()

    with col5:
        with st.container(border=True):
            st.markdown(f'''
            <div class="card-badge">📈 ADS PILOT</div>
            <div class="card-subtitle-sub">/social-ads-pilot</div>
            <div class="card-title-main">{clean_titles['ads']}</div>
            <p class="card-desc-text">{descs['ads']}</p>
            ''', unsafe_allow_html=True)
            if st.button(btn_label, key="enter_ads", use_container_width=True, type="primary"):
                st.session_state.current_page = "ads"
                st.rerun()

    with col6:
        with st.container(border=True):
            st.markdown(f'''
            <div class="card-badge">📚 SOP MANUAL</div>
            <div class="card-subtitle-sub">/sop-clearance-manual</div>
            <div class="card-title-main">{clean_titles['training']}</div>
            <p class="card-desc-text">{descs['training']}</p>
            ''', unsafe_allow_html=True)
            if st.button(btn_label, key="enter_training", use_container_width=True, type="primary"):
                st.session_state.current_page = "training"
                st.rerun()

# Execute layout routing
if st.session_state.current_page == "home":
    render_homepage()
    st.stop()
else:
    render_navbar()

# ---------------------------------------------------------
# Tab 1: 西非本土化营销文案生成器 (Text-to-Copy)
# ---------------------------------------------------------
if st.session_state.current_page == "copy":
    render_dashboard_header(L['t1_header'], L['t1_desc'], "Console // Copywriter")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.container(border=True):
            st.markdown(f"### <i class='fa-solid fa-keyboard'></i> {L['t1_input_header']}", unsafe_allow_html=True)
            
            # Retrieve categories and selling points lists from st.session_state
            categories = st.session_state.categories_dict[sys_lang]
            points_options = st.session_state.points_dict[sys_lang]
            points_default = [pt for pt in st.session_state.points_defaults[sys_lang] if pt in points_options]
                
            # Find default index of st.session_state.prod_category in categories to keep sync
            try:
                cat_index = categories.index(st.session_state.prod_category)
            except ValueError:
                cat_index = 0
            prod_category = st.selectbox(L["t1_cat"], categories, index=cat_index)
            st.session_state.prod_category = prod_category

            prod_name = st.text_input(L["t1_name"], value="Heavy Duty Plastic Stackable Chair (35*35*80cm)")
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                clearance_price = st.number_input(L["t1_price"], min_value=1, value=12500, step=500, key="t1_price_in")
            with c_col2:
                moq_qty = st.number_input(L["t1_moq"], min_value=1, value=50, step=10, key="t1_moq_in")
                
            sell_points = st.multiselect(L["t1_points"], points_options, default=points_default, key="t1_points_in")
            extra_info = st.text_input(L["t1_extra"], value="Only 350 units left in Lagos stock, clearing this week!", key="t1_extra_in")
            
            use_pidgin = st.checkbox(L["t1_pidgin"], value=True, help=L["t1_pidgin_help"])
            
            generate_btn = st.button(L["t1_btn"], type="primary")
            
            # Expander for dynamic management of categories and selling points
            with st.expander(L["manage_expander"]):
                # Display persistent status message if it exists
                if "status_message" in st.session_state and st.session_state.status_message:
                    msg_type, msg_text = st.session_state.status_message
                    if msg_type == "success":
                        st.success(msg_text)
                    elif msg_type == "warning":
                        st.warning(msg_text)
                    elif msg_type == "error":
                        st.error(msg_text)
                    st.session_state.status_message = None  # Clear it so it only shows once

                st.markdown(f"##### 📁 {L['t1_cat']}")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    new_cat = st.text_input(L["add_cat"], key="new_cat_input")
                    if st.button(L["add_btn"], key="add_cat_btn"):
                        if new_cat.strip():
                            new_cat_val = new_cat.strip()
                            if new_cat_val not in st.session_state.categories_dict[sys_lang]:
                                # Add to all languages with translation
                                for lang in ["简体中文", "English", "Nigerian Pidgin"]:
                                    if lang == sys_lang:
                                        st.session_state.categories_dict[lang].append(new_cat_val)
                                    else:
                                        translated = translate_text(new_cat_val, lang)
                                        st.session_state.categories_dict[lang].append(translated)
                                save_persistent_data()
                                st.session_state.status_message = ("success", f"{L['success_add_cat']}{new_cat_val}")
                                st.rerun()
                            else:
                                st.session_state.status_message = ("warning", L["dup_warn"])
                                st.rerun()
                        else:
                            st.session_state.status_message = ("warning", L["empty_warn"])
                            st.rerun()
                with col_c2:
                    del_cat_target = st.selectbox(L["del_cat"], categories, key="del_cat_select")
                    if st.button(L["del_btn"], key="del_cat_btn"):
                        if del_cat_target in st.session_state.categories_dict[sys_lang]:
                            try:
                                idx = st.session_state.categories_dict[sys_lang].index(del_cat_target)
                                for lang in ["简体中文", "English", "Nigerian Pidgin"]:
                                    if idx < len(st.session_state.categories_dict[lang]):
                                        st.session_state.categories_dict[lang].pop(idx)
                                save_persistent_data()
                                st.session_state.status_message = ("success", f"{L['success_del_cat']}{del_cat_target}")
                                st.rerun()
                            except Exception as e:
                                st.session_state.status_message = ("error", f"Error: {e}")
                                st.rerun()
                            
                st.markdown("---")
                st.markdown(f"##### 🏷️ {L['t1_points']}")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    new_point = st.text_input(L["add_pt"], key="new_point_input")
                    if st.button(L["add_btn"], key="add_pt_btn"):
                        if new_point.strip():
                            new_point_val = new_point.strip()
                            if new_point_val not in st.session_state.points_dict[sys_lang]:
                                # Add to all languages with translation
                                for lang in ["简体中文", "English", "Nigerian Pidgin"]:
                                    if lang == sys_lang:
                                        st.session_state.points_dict[lang].append(new_point_val)
                                        st.session_state.points_defaults[lang].append(new_point_val)
                                    else:
                                        translated = translate_text(new_point_val, lang)
                                        st.session_state.points_dict[lang].append(translated)
                                        st.session_state.points_defaults[lang].append(translated)
                                save_persistent_data()
                                st.session_state.status_message = ("success", f"{L['success_add_pt']}{new_point_val}")
                                st.rerun()
                            else:
                                st.session_state.status_message = ("warning", L["dup_warn"])
                                st.rerun()
                        else:
                            st.session_state.status_message = ("warning", L["empty_warn"])
                            st.rerun()
                with col_p2:
                    del_point_target = st.selectbox(L["del_pt"], points_options, key="del_pt_select")
                    if st.button(L["del_btn"], key="del_pt_btn"):
                        if del_point_target in st.session_state.points_dict[sys_lang]:
                            try:
                                idx = st.session_state.points_dict[sys_lang].index(del_point_target)
                                for lang in ["简体中文", "English", "Nigerian Pidgin"]:
                                    if idx < len(st.session_state.points_dict[lang]):
                                        val_to_del = st.session_state.points_dict[lang].pop(idx)
                                        if val_to_del in st.session_state.points_defaults[lang]:
                                            st.session_state.points_defaults[lang].remove(val_to_del)
                                save_persistent_data()
                                st.session_state.status_message = ("success", f"{L['success_del_pt']}{del_point_target}")
                                st.rerun()
                            except Exception as e:
                                st.session_state.status_message = ("error", f"Error: {e}")
                                st.rerun()

            # Pidgin glossary tips
            with st.expander(L["glossary_title"]):
                st.markdown(f"""
                | {L['glossary_th_slang']} | {L['glossary_th_meaning']} | {L['glossary_th_purpose']} |
                | :--- | :--- | :--- |
                | **Na double quality** | Extremely strong / double quality | Tells local buyer that the goods won't break easily. |
                | **Aje / Aje o** | I swear it is authentic / genuine | Builds trust directly with skeptical local buyers. |
                | **Chop life price** | Insanely cheap clearance price | Triggers impulse buying for local wholesalers. |
                | **No story / No stories** | Direct honest deal, zero deposit scam | Assures they can pay on delivery or pick up directly. |
                | **Correct quality** | Genuine imported standard | Signals high grade container arrivals. |
                """)

    with col2:
        with st.container(border=True):
            st.markdown(f"### <i class='fa-solid fa-wand-magic-sparkles'></i> {L['t1_out_header']}", unsafe_allow_html=True)
            
            if generate_btn:
                system_prompt = """You are a top-tier cross-border e-commerce copywriter specialized in West Africa, especially the Nigerian B2B/B2C wholesale market.
Your task is to write highly engaging, energetic, and high-converting marketing copywriting in English.

CRITICAL STYLE REQUIREMENTS:
1. Output copy MUST BE PURE ENGLISH.
2. Tone: Extremely dramatic, high energy, urgent, and loud.
3. Emojis: Use plenty of emojis to attract attention (🔥, 💥, 🚨, 😱, 📦, 📍, 📞).
4. Essential information to include:
   - Clear pricing in NGN.
   - Wholesale terms and MOQ (Minimum Order Quantity).
   - Logistics options: Lagos warehouse self-pickup or Cash on Delivery (COD).
   - Urgent scarcity elements ("Only X left", "Container clearance")."""

                if use_pidgin:
                    system_prompt += """
5. Since the user requested West African Pidgin/Slang tuning, you must naturalize the copy by incorporating local slang expressions where appropriate. Use phrases like:
   - 'Na double quality' (to emphasize durability/strength)
   - 'Aje' / 'Aje o' (to promise authenticity)
   - 'Chop life price' (insanely good deal)
   - 'No story / No stories' (straightforward warehouse deal, no deposit scams)
   - 'Correct quality' (premium import quality)
Keep the base copywriting in English, but sprinkle these local pidgin elements to make it sound like a local Nigerian reseller advertisement."""

                system_prompt += """
                
Generate exactly 3 styles of copies:
Style 1: [💥 URGENT CLEARANCE / 紧急清仓风] - Heavy focus on price slash, limited quantity, and warehouse eviction pressure.
Style 2: [💎 BUSINESS PARTNER PORTAL / 代理招商商机风] - Highlight profit margins for local resellers/retailers, quality check, and bulk savings.
Style 3: [📱 WHATSAPP & SOCIAL SHORT CUT / 快捷直销风] - Bullet points, short paragraphs, perfect for copy-pasting to WhatsApp Status, Facebook Groups, or Jiji.ng.

Structure the final output in clear markdown sections. Do not use Chinese in the generated copies, but keep the headers in English and Chinese."""

                user_prompt = f"""
Category: {prod_category}
Product Name & Spec: {prod_name}
Clearance Price: {clearance_price} NGN
MOQ: {moq_qty} units
Key Selling Points: {', '.join(sell_points)}
Extra comments: {extra_info}
WhatsApp Contact: {watermark_phone}
Lagos Pickup Address: {lagos_address}
Pidgin Slang Mode: {"ENABLED" if use_pidgin else "DISABLED"}
"""
                
                with st.spinner("AI is brainstorming West African copies..." if sys_lang != "简体中文" else "AI 正在深度解构西非语境，为您撰写清仓文案..."):
                    response = call_llm(
                        system_prompt, 
                        user_prompt, 
                        lambda: get_mock_marketing_copy(prod_name, prod_category, clearance_price, moq_qty, sell_points, extra_info, watermark_phone, use_pidgin)
                    )
                    st.session_state.marketing_copy = response
            
            if st.session_state.marketing_copy:
                st.markdown(st.session_state.marketing_copy)
            else:
                st.info(L["t1_info"])
            
        # Facebook mockup rendering
        if st.session_state.marketing_copy:
            st.markdown(f"### <i class='fa-solid fa-display'></i> {L['t1_mock_title']}", unsafe_allow_html=True)
            st.write(L["t1_mock_desc"])
            
            try:
                ad_text_sample = "💥 LAGOS CLEARANCE IMPORTER CONTAINER LIQUIDATION! 💥\n" + st.session_state.marketing_copy.split("Style 1:")[1].split("Style 2:")[0].replace("#### 💥 紧急抛售风 (Urgent Clearance - High Scarcity)", "").strip()
            except Exception:
                ad_text_sample = st.session_state.marketing_copy[:300]
                
            img_b64 = get_base64_image(st.session_state.processed_image)
            st.markdown(render_fb_ad_mockup(ad_text_sample, img_b64, watermark_phone), unsafe_allow_html=True)

# ---------------------------------------------------------
# Tab 2: 图像去噪与水印 (Image-to-Product)
# ---------------------------------------------------------
if st.session_state.current_page == "image":
    render_dashboard_header(L['t2_header'], L['t2_desc'], "Console // Image Editor")
    
    t2_sub_tab1, t2_sub_tab2 = st.tabs([
        "一键抠图与水印" if sys_lang == "简体中文" else "Clean & Watermark",
        "AI 智能生图" if sys_lang == "简体中文" else "AI Image Generation"
    ])
    
    with t2_sub_tab1:
        col_img1, col_img2 = st.columns([1, 1])

        with col_img1:
            with st.container(border=True):
                st.markdown(f'### <i class="fa-solid fa-cloud-arrow-up"></i> {L["t2_input_header"]}', unsafe_allow_html=True)

                uploaded_files = st.file_uploader(L["t2_file_label"], type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="t2_upload_files")

                st.markdown(f"##### <i class='fa-solid fa-sliders'></i> {L['t2_wm_header']}", unsafe_allow_html=True)
                phone_for_watermark = st.text_input(L["t2_wm_phone"], value=watermark_phone, key="t2_phone_in")
                apply_wm = st.checkbox(L["t2_wm_apply"], value=True, key="t2_apply_in")

                # Check if WhatsApp QR code exists in workspace
                qr_exists = os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_qrcode.png"))
                apply_qr = st.checkbox(
                    L["t2_wm_qr"],
                    value=qr_exists,
                    disabled=not qr_exists,
                    help="如果检测到企业WhatsApp二维码，可选择加盖到图片右下角" if sys_lang == "简体中文" else "Applies WhatsApp QR code to the bottom-right corner if available.",
                    key="t2_apply_qr"
                )

                # Background removal method selection
                if sys_lang == "简体中文":
                    bg_methods = [
                        "isnet-general-use (高精度通用模型 - 推荐)",
                        "u2net (标准通用模型)",
                        "腾讯云数据万象 (通用抠图 AIPicMatting)",
                        "腾讯云数据万象 (商品抠图 GoodsMatting)",
                        "关闭去背景 (仅加水印)"
                    ]
                elif sys_lang == "English":
                    bg_methods = [
                        "isnet-general-use (High Accuracy - Recommended)",
                        "u2net (Standard Local)",
                        "Tencent Cloud CI (General Matting - AIPicMatting)",
                        "Tencent Cloud CI (Goods Matting - GoodsMatting)",
                        "Skip Background Removal (Watermark only)"
                    ]
                else:
                    bg_methods = [
                        "isnet-general-use (High Quality - Best)",
                        "u2net (Normal Local)",
                        "Tencent Cloud CI (General Matting)",
                        "Tencent Cloud CI (Goods Matting)",
                        "No clean background (Watermark only)"
                    ]


                removebg_method = st.selectbox(
                    L["t2_bg_method_label"],
                    bg_methods,
                    index=0,
                    key="t2_removebg_method"
                )



                # i18n watermark positions options
                if sys_lang == "简体中文":
                    positions = [
                        "右下角 (Bottom-Right)",
                        "左下角 (Bottom-Left)",
                        "右上角 (Top-Right)",
                        "左上角 (Top-Left)",
                        "居中 (Center)",
                        "全图斜网格平铺防盗 (Tile Overlay)"
                    ]
                    colors = [
                        "极光紫 (Violet)",
                        "深海蓝 (Blue)",
                        "警示红 (Red)",
                        "碳灰色 (Charcoal)"
                    ]
                elif sys_lang == "English":
                    positions = [
                        "Bottom-Right",
                        "Bottom-Left",
                        "Top-Right",
                        "Top-Left",
                        "Center",
                        "Tile Overlay"
                    ]
                    colors = [
                        "Violet",
                        "Blue",
                        "Red",
                        "Charcoal"
                    ]
                else: # Pidgin
                    positions = [
                        "Down Right side",
                        "Down Left side",
                        "Up Right side",
                        "Up Left side",
                        "Inside Center",
                        "Tile Overlay (Full Screen)"
                    ]
                    colors = [
                        "Violet light",
                        "Blue ocean",
                        "Red alert",
                        "Charcoal dark"
                    ]

                wm_position = st.selectbox(L["t2_wm_pos"], positions)
                wm_color = st.selectbox(L["t2_wm_color"], colors)
                wm_scale = st.slider(L["t2_wm_scale"], min_value=1.5, max_value=6.0, value=3.5, step=0.5)

                st.markdown("---")
                st.markdown(f"##### <i class='fa-solid fa-wand-magic-sparkles'></i> {L['t2_template_label']}", unsafe_allow_html=True)

                template_options = [
                    L["t2_template_none"],
                    L["t2_template_banner"],
                    L["t2_template_stamp"]
                ]
                wm_template = st.selectbox(L["t2_template_label"], template_options, index=0, label_visibility="collapsed")

                # Show price and MOQ inputs if banner is selected
                t2_price = 12500
                t2_moq = 50
                if wm_template == L["t2_template_banner"]:
                    t2_c1, t2_c2 = st.columns(2)
                    with t2_c1:
                        t2_price = st.number_input(L["t2_price_label"], min_value=0, value=12500, step=500)
                    with t2_c2:
                        t2_moq = st.number_input(L["t2_moq_label"], min_value=0, value=50, step=5)

                process_btn = st.button(L["t2_btn"], type="primary")

        with col_img2:
            with st.container(border=True):
                st.markdown(f'### <i class="fa-solid fa-images"></i> {L["t2_out_header"]}', unsafe_allow_html=True)

                if "t2_persistent_files" not in st.session_state:
                    st.session_state.t2_persistent_files = []
                if "processed_images" not in st.session_state:
                    st.session_state.processed_images = {}

                # Save uploaded files into session state to survive tab switching
                if uploaded_files:
                    batch_key = "|".join([f"{f.name}_{f.size}" for f in uploaded_files])
                    if st.session_state.get("t2_current_batch_key") != batch_key:
                        st.session_state.t2_current_batch_key = batch_key
                        st.session_state.processed_images = {}  # Clear dictionary cache
                        st.session_state.t2_persistent_files = []
                        for f in uploaded_files:
                            st.session_state.t2_persistent_files.append({
                                "name": f.name,
                                "content": f.getvalue(),
                                "size": f.size
                            })

                active_files = uploaded_files if uploaded_files else st.session_state.t2_persistent_files

                if active_files:
                    # If uploader is empty but we have persistent session files, show helper text
                    if not uploaded_files:
                        st.info("💡 已为您保留上一次的抠图与水印处理历史。如果您想处理新图片，请直接在左侧上传新文件。" if sys_lang == "简体中文" else "💡 Last processed session has been restored. Upload new files on the left if you want to start a new batch.")

                    # Loop and process files if process_btn is clicked
                    if process_btn:
                        with st.spinner("AI is cleaning raw background..." if sys_lang != "简体中文" else "🚀 AI 图像净化与抠图引擎正在运行中..."):
                            for f in active_files:
                                f_name = f.name if hasattr(f, "name") else f["name"]
                                f_data = io.BytesIO(f.getvalue()) if hasattr(f, "getvalue") else io.BytesIO(f["content"])
                                processed_img = process_warehouse_image_advanced(
                                    f_data, 
                                    phone_for_watermark, 
                                    apply_wm,
                                    wm_position,
                                    wm_color,
                                    wm_scale,
                                    template_type=wm_template,
                                    price=t2_price,
                                    moq=t2_moq,
                                    apply_qr=apply_qr,
                                    removebg_method=removebg_method
                                )
                                if processed_img:
                                    buf = io.BytesIO()
                                    processed_img.save(buf, format="JPEG")
                                    st.session_state.processed_images[f_name] = (processed_img, buf.getvalue())

                    # Display results for all selected files together
                    for idx, f in enumerate(active_files):
                        f_name = f.name if hasattr(f, "name") else f["name"]
                        f_raw = f if hasattr(f, "read") else io.BytesIO(f["content"])
                        st.markdown(f"<p style='font-size: 0.95rem; font-weight: 500; color: #a3a3a3; margin-top: 15px; margin-bottom: 2px; word-break: break-all;'>📄 Image {idx + 1}: {f_name}</p>", unsafe_allow_html=True)
                        o_col, p_col = st.columns(2)
                        with o_col:
                            st.image(f_raw, caption=L["t2_orig"], use_container_width=True)

                        with p_col:
                            if f_name in st.session_state.processed_images:
                                proc_img, proc_bytes = st.session_state.processed_images[f_name]
                                st.image(proc_img, caption=L["t2_proc"], use_container_width=True)

                                col_dl, col_re = st.columns(2)
                                with col_dl:
                                    st.download_button(
                                        label=L["t2_download"],
                                        data=proc_bytes,
                                        file_name=f"cleared_{f_name}",
                                        mime="image/jpeg",
                                        key=f"dl_{f_name}_{idx}",
                                        use_container_width=True
                                    )
                                with col_re:
                                    reprocess_btn = st.button(L.get("t2_regenerate", "🔄 Regenerate"), key=f"re_{f_name}_{idx}", type="secondary", use_container_width=True)
                                    if reprocess_btn:
                                        with st.spinner("AI is cleaning raw background..." if sys_lang != "简体中文" else "🚀 AI 图像净化与抠图引擎正在运行中..."):
                                            f_raw_re = f if hasattr(f, "read") else io.BytesIO(f["content"])
                                            processed_img = process_warehouse_image_advanced(
                                                f_raw_re, 
                                                phone_for_watermark, 
                                                apply_wm,
                                                wm_position,
                                                wm_color,
                                                wm_scale,
                                                template_type=wm_template,
                                                price=t2_price,
                                                moq=t2_moq,
                                                apply_qr=apply_qr,
                                                removebg_method=removebg_method
                                            )
                                            if processed_img:
                                                buf = io.BytesIO()
                                                processed_img.save(buf, format="JPEG")
                                                st.session_state.processed_images[f_name] = (processed_img, buf.getvalue())
                                                st.rerun()
                            else:
                                st.warning(L["t2_warn"])
                        st.markdown("---")
                else:
                    st.info(L["t2_info"])

    # ---------------------------------------------------------
    # Tab 3: WhatsApp 客服话术 (SOP Hub)
    # ---------------------------------------------------------

    with t2_sub_tab2:
        col_gen1, col_gen2 = st.columns([1, 1])
        
        with col_gen1:
            with st.container(border=True):
                st.markdown(f'### <i class="fa-solid fa-wand-magic-sparkles"></i> ' + ("AI 智能生图" if sys_lang == "简体中文" else "AI Image Generation"), unsafe_allow_html=True)
                
                # Reference image persistence logic
                if "t2_gen_persistent_ref" not in st.session_state:
                    st.session_state.t2_gen_persistent_ref = None
                
                # reference image upload (optional)
                gen_ref_file = st.file_uploader(
                    "📎 上传参考图片 (例如：女装/商品图)" if sys_lang == "简体中文" else "📎 Upload Reference Image (e.g., clothing/product)", 
                    type=["jpg", "jpeg", "png"], 
                    key="t2_gen_ref_image"
                )
                
                if gen_ref_file:
                    st.session_state.t2_gen_persistent_ref = {
                        "name": gen_ref_file.name,
                        "content": gen_ref_file.getvalue()
                    }
                
                active_ref = None
                if gen_ref_file:
                    active_ref = st.session_state.t2_gen_persistent_ref
                elif st.session_state.t2_gen_persistent_ref:
                    active_ref = st.session_state.t2_gen_persistent_ref
                    st.info("💡 已为您保留上一次的参考图片。如需更换，请直接在左侧上传新文件。" if sys_lang == "简体中文" else "💡 Reference image restored. Upload a new file on the left to replace it.")
                
                # text area for prompt (large box)
                if "t2_gen_prompt_val" not in st.session_state:
                    st.session_state.t2_gen_prompt_val = "一个年轻漂亮的尼日利亚女模特身穿这件衣服，在专业摄影棚内拍摄，专业影棚柔和光影，高清画质，时尚大片效果"
                
                gen_prompt = st.text_area(
                    "✍️ 输入生成提示词" if sys_lang == "简体中文" else "✍️ Enter Generation Prompt",
                    value=st.session_state.t2_gen_prompt_val,
                    placeholder="描述您想要生成的场景和细节。例如：\n一个尼日利亚女模特身穿这件衣服在拉各斯繁华市中心摆姿势，阳光明媚，虚化背景，高分辨率时尚大片。" if sys_lang == "简体中文" else "Describe your target scene. e.g.,\nA Nigerian female model wearing this clothing, posing in downtown Lagos, sunny day, bokeh background, high fashion photography.",
                    height=180,
                    key="t2_gen_prompt_temp"
                )
                st.session_state.t2_gen_prompt_val = gen_prompt
                
                # model selection info
                st.info(f"🤖 **Image Model / 图像模型:** `{openai_image_model}`" if sys_lang == "简体中文" else f"🤖 **Image Model:** `{openai_image_model}`")
                
                btn_gen = st.button("🚀 开始生成 / Generate Image", type="primary", use_container_width=True, key="t2_btn_gen_img_submit")
                
        with col_gen2:
            with st.container(border=True):
                st.markdown(f'### <i class="fa-solid fa-image"></i> ' + ("生成结果" if sys_lang == "简体中文" else "Generation Result"), unsafe_allow_html=True)
                
                # session states for generated image
                if "t2_gen_image_data" not in st.session_state:
                    st.session_state.t2_gen_image_data = ""
                if "t2_gen_image_is_b64" not in st.session_state:
                    st.session_state.t2_gen_image_is_b64 = False
                if "t2_generated_image_prompt" not in st.session_state:
                    st.session_state.t2_generated_image_prompt = ""
                if "t2_gen_running" not in st.session_state:
                    st.session_state.t2_gen_running = False
                if "t2_gen_start_time" not in st.session_state:
                    st.session_state.t2_gen_start_time = 0.0
                if "t2_gen_result_dict" not in st.session_state:
                    st.session_state.t2_gen_result_dict = {}
                if "t2_gen_error" not in st.session_state:
                    st.session_state.t2_gen_error = None

                # Background thread runner function
                def bg_generate_image_thread(prompt, ref_bytes, result_dict):
                    try:
                        data, used_prompt, is_b64 = generate_image_gpt_image_2(prompt, ref_bytes)
                        result_dict["data"] = data
                        result_dict["used_prompt"] = used_prompt
                        result_dict["is_b64"] = is_b64
                        result_dict["error"] = None
                    except Exception as e:
                        result_dict["error"] = str(e)
                    finally:
                        result_dict["done"] = True

                if btn_gen:
                    if not gen_prompt.strip():
                        st.error("请输入生成提示词！" if sys_lang == "简体中文" else "Please enter a generation prompt!")
                    elif st.session_state.t2_gen_running:
                        st.warning("已有图片正在生成中，请耐心等待完成！" if sys_lang == "简体中文" else "An image is already generating, please wait!")
                    else:
                        ref_bytes = None
                        if active_ref:
                            ref_bytes = active_ref["content"]
                        
                        # Set up background thread states
                        st.session_state.t2_gen_running = True
                        st.session_state.t2_gen_start_time = time.time()
                        st.session_state.t2_gen_image_data = ""
                        st.session_state.t2_gen_image_is_b64 = False
                        st.session_state.t2_generated_image_prompt = ""
                        st.session_state.t2_gen_error = None
                        st.session_state.t2_gen_result_dict = {"done": False, "data": None, "used_prompt": None, "is_b64": False, "error": None}
                        
                        thread = threading.Thread(
                            target=bg_generate_image_thread,
                            args=(gen_prompt, ref_bytes, st.session_state.t2_gen_result_dict),
                            daemon=True
                        )
                        thread.start()
                        st.rerun()

                # Process running state or results
                if st.session_state.t2_gen_running:
                    res_dict = st.session_state.t2_gen_result_dict
                    if res_dict.get("done", False):
                        # Task finished!
                        st.session_state.t2_gen_running = False
                        if res_dict.get("error"):
                            st.session_state.t2_gen_error = res_dict["error"]
                            st.session_state.t2_gen_image_data = ""
                        else:
                            st.session_state.t2_gen_image_data = res_dict["data"]
                            st.session_state.t2_gen_image_is_b64 = res_dict["is_b64"]
                            st.session_state.t2_generated_image_prompt = res_dict["used_prompt"]
                            st.session_state.t2_gen_error = None
                            st.success("生成成功！" if sys_lang == "简体中文" else "Generated successfully!")
                        st.rerun()

                # Error display block
                if st.session_state.t2_gen_error:
                    st.error(f"生成失败 / Generation failed: {st.session_state.t2_gen_error}")

                if st.session_state.t2_gen_running:
                    # 1. Warning message
                    st.warning("⚠️ 由于此生成图片需要3-5分钟一张，请勿刷新网页，请耐心等待 / Since generating this image takes 3-5 minutes, please do not refresh and wait patiently...")
                    
                    # 3. Calculate elapsed time
                    elapsed = int(time.time() - st.session_state.t2_gen_start_time)
                    m, s = divmod(elapsed, 60)
                    time_str = f"{m:02d}:{s:02d}"
                    
                    # 2. Display progress bar (fake creeping progress starting at 1%, increments every second, max 99%)
                    progress_val = min(99, 1 + int(elapsed * 0.5))
                    
                    st.progress(progress_val / 100.0)
                    
                    # Display elapsed time and progress value
                    st.write(f"⏱️ **已用时间 / Time Elapsed:** `{time_str}` &nbsp;&nbsp;&nbsp;&nbsp; 📈 **估计进度 / Progress:** `{progress_val}%`", unsafe_allow_html=True)
                    
                    # Sleep and rerun to update timer
                    time.sleep(1)
                    st.rerun()

                elif st.session_state.t2_gen_image_data:
                    import base64
                    
                    if st.session_state.t2_gen_image_is_b64:
                        try:
                            img_bytes = base64.b64decode(st.session_state.t2_gen_image_data)
                            st.image(img_bytes, use_container_width=True)
                            
                            st.download_button(
                                label="📥 下载生成图片 / Download Image",
                                data=img_bytes,
                                file_name="generated_image.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        except Exception as render_err:
                            st.error(f"Image decode/render error: {render_err}")
                    else:
                        st.image(st.session_state.t2_gen_image_data, use_container_width=True)
                        
                        try:
                            import requests
                            img_res = requests.get(st.session_state.t2_gen_image_data)
                            if img_res.status_code == 200:
                                st.download_button(
                                    label="📥 下载生成图片 / Download Image",
                                    data=img_res.content,
                                    file_name="generated_image.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                        except Exception as download_err:
                            st.markdown(f"[🔗 点击此处打开并保存图片 / Click to Open Image]({st.session_state.t2_gen_image_data})")
                    
                    if st.session_state.t2_generated_image_prompt:
                        with st.expander("📝 优化后的最终提示词 / Optimized Final Prompt"):
                            st.write(st.session_state.t2_generated_image_prompt)
                else:
                    if not st.session_state.t2_gen_error:
                        st.info("生成后的图片将在此处显示。" if sys_lang == "简体中文" else "Generated image will be displayed here.")
if st.session_state.current_page == "sop":
    render_dashboard_header(L['t3_header'], L['t3_desc'], "Console // Customer SOP")
    
    with st.container(border=True):
        st.markdown(f'### <i class="fa-solid fa-circle-info"></i> {L["t3_setting_header"]}', unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            active_prod = st.text_input(L["t3_active_prod"], value=st.session_state.active_prod)
            st.session_state.active_prod = active_prod
        with sc2:
            active_price = st.number_input(L["t3_active_price"], min_value=1, value=st.session_state.active_price)
            st.session_state.active_price = active_price
        with sc3:
            active_moq = st.number_input(L["t3_active_moq"], min_value=1, value=st.session_state.active_moq)
            st.session_state.active_moq = active_moq    
    sop_cats = st.tabs([
        L["t3_subtab_price"],
        L["t3_subtab_addr"],
        L["t3_subtab_moq"],
        L["t3_subtab_pay"],
        L["t3_subtab_urg"]
    ])
    
    with sop_cats[0]:
        st.markdown(f"##### <i class='fa-solid fa-tags'></i> {L['t3_scen1']}", unsafe_allow_html=True)
        t1 = f"Hello! Yes, the {active_prod} is fully available in our Lagos warehouse. The wholesale clearance price is {active_price:,} NGN per unit. Note that this is direct importer wholesale price, normally sold at {int(active_price*1.5):,} NGN in markets. Our MOQ is {active_moq} units. Are you buying for your retail shop or warehouse? Let me know so I can reserve stock for you. 📞 WhatsApp: {watermark_phone}."
        st.code(t1, language="text")
        st.markdown(f"##### <i class='fa-solid fa-mobile-screen'></i> {L['t3_mock_label']}", unsafe_allow_html=True)
        st.markdown(render_wa_chat_mockup("How much is the chair and what's the minimum quantity? Can I buy one?", t1), unsafe_allow_html=True)
        
    with sop_cats[1]:
        st.markdown(f"##### <i class='fa-solid fa-map-location-dot'></i> {L['t3_scen2']}", unsafe_allow_html=True)
        t2 = f"Yes, you are 100% welcome to inspect the goods first! We encourage self-pickup at our Lagos warehouse. Here is the address:\n📍 Address: {lagos_address}\n⏰ Working Hours: Monday to Saturday, 9:00 AM - 5:00 PM\n📞 Please call our warehouse manager at {watermark_phone} 30 minutes before you arrive so we can prepare your gate pass and load your truck."
        st.code(t2, language="text")
        st.markdown(f"##### <i class='fa-solid fa-mobile-screen'></i> {L['t3_mock_label']}", unsafe_allow_html=True)
        st.markdown(render_wa_chat_mockup("I want to come check the quality first. Where is your Lagos warehouse?", t2), unsafe_allow_html=True)
        
    with sop_cats[2]:
        st.markdown(f"##### <i class='fa-solid fa-circle-exclamation'></i> {L['t3_scen3']}", unsafe_allow_html=True)
        t3 = f"Sorry, please understand we are a direct container clearance warehouse, not a retail shop. Selling single pieces will cost us too much operational time. The strict MOQ is {active_moq} units. That is why our price is {active_price:,} NGN—which is almost 40% cheaper than the local open markets. If you cannot buy {active_moq} units, you can combine orders with other traders near you to share the wholesale price. Let me know if you want to place the container batch."
        st.code(t3, language="text")
        st.markdown(f"##### <i class='fa-solid fa-mobile-screen'></i> {L['t3_mock_label']}", unsafe_allow_html=True)
        st.markdown(render_wa_chat_mockup("The minimum 50 is too much for me. Can you sell me 5 pieces at the same price?", t3), unsafe_allow_html=True)
        
    with sop_cats[3]:
        st.markdown(f"##### <i class='fa-solid fa-shield-halved'></i> {L['t3_scen4']}", unsafe_allow_html=True)
        # Extract bank name if possible
        extracted_bank = "Sterling Bank PLC"
        try:
            if " - " in account_number:
                extracted_bank = account_number.split(" - ")[-1].strip()
        except Exception:
            pass
        t4 = f"⚠️ ANTI-FRAUD NOTICE: To secure your transaction, please verify our details. We ONLY accept payments to our registered corporate bank account. Do NOT pay any individual agent or rider.\n\n- Bank Name: {extracted_bank}\n- Account Name: {account_name}\n- Account Number: {account_number.split(' - ')[0] if ' - ' in account_number else account_number}\n\nOnce transferred, send the receipt here. Our finance team will confirm immediately and generate your gate pass. Cash on Delivery is also accepted for self-pickup at our Lagos warehouse."
        st.code(t4, language="text")
        st.markdown(f"##### <i class='fa-solid fa-mobile-screen'></i> {L['t3_mock_label']}", unsafe_allow_html=True)
        st.markdown(render_wa_chat_mockup("Okay send me bank details. I want to pay for the 50 chairs.", t4), unsafe_allow_html=True)
        
    with sop_cats[4]:
        st.markdown(f"##### <i class='fa-solid fa-hourglass-half'></i> {L['t3_scen5']}", unsafe_allow_html=True)
        t5 = f"Hello chief! Just checking on your order for {active_prod}. Our warehouse is clearing this container fast, and we only have few units left at {active_price:,} NGN. A reseller just booked a big batch. If you want to lock the price and quantity, you can make a small commitment transfer to our corporate account. Let me know if I should prepare your invoice now. First come, first served!"
        st.code(t5, language="text")
        st.markdown(f"##### <i class='fa-solid fa-mobile-screen'></i> {L['t3_mock_label']}", unsafe_allow_html=True)
        st.markdown(render_wa_chat_mockup("I am still thinking. I will message you next week.", t5), unsafe_allow_html=True)

# ---------------------------------------------------------
# Tab 4: 爆款视频本土化 (Video-to-Local-Script)
# ---------------------------------------------------------
if st.session_state.current_page == "video":
    # Multi-language definitions for Creatok style interface
    T4_UI = {
        "简体中文": {
            "center_title": "分析、复刻或生成爆款带货视频",
            "center_desc": "上传参考视频、产品图片或输入核心卖点，AI 会拆解运镜逻辑并生成适合您产品的拍摄分镜。",
            "offer_config": "商品与报价配置（独立功能）",
            "create": "创作爆款",
            "replicate": "复刻爆款",
            "analyze": "分析脚本",
            "visual": "视频拆解复刻",
            "upload": "上传视频",
            "uploaded": "视频已上传",
            "link": "添加链接",
            "link_added": "链接已添加",
            "images": "产品图片",
            "images_open": "产品图已打开",
            "run": "开始 AI 重构",
            "video_url": "视频链接",
            "upload_video": "上传短视频文件",
            "upload_images": "上传自己的产品图片",
            "scene": "拍摄场景",
            "target_seconds": "目标秒数",
            "script_label": "视频脚本 / 产品信息",
            "create_placeholder": "输入您的商品卖点...",
            "replicate_placeholder": "输入您想复刻的视频描述或脚本配音内容...",
            "analyze_placeholder": "粘贴您想分析的中文原版文案...",
            "visual_placeholder": "说明你想保留的运镜逻辑，以及你的产品/套餐/场景要求...",
            "extracting": "正在抽帧拆解上传视频...",
            "url_processing": "正在解析视频链接元数据及音频轨道...",
            "thinking": "AI 正在拆解并生成拍摄分镜...",
            "keyframes": "上传视频关键帧拆解",
            "keyframes_caption": "参考视频关键帧",
            "storyboard": "分镜脚本",
            "assistant": "AI 剧本协同设计助理",
            "chat_placeholder": "向我提问任何与视频相关的问题...",
            "system_status": "系统提示",
            "generated_msg": "已为您生成 **{product}** 的拍摄分镜与结构拆解。\n\n{status}\n\n您可以在下方直接发送调整指令继续修改。",
            "no_video": "未检测到上传参考视频。请上传视频以进行视觉拆解；当前先按文本和产品图片生成。",
            "video_error": "上传视频拆解失败: {error}。已降级为使用文本和产品图片生成。",
            "audio_unsupported": "当前 API Key 代理不支持语音转文字 (whisper-1)。已自动降级为使用视频标题及描述元数据进行重构。",
            "audio_missing": "未能成功下载视频音频轨道。已自动降级为使用视频标题及描述元数据进行重构。",
            "url_error": "视频解析错误: {error}。已使用您粘贴的文本进行重构。",
            "output_language": "简体中文",
        },
        "English": {
            "center_title": "Analyze, Replicate or Generate Viral Videos",
            "center_desc": "Upload a reference video, product images, or product details. AI will break down the filming logic and generate a storyboard for your own product.",
            "offer_config": "Product & Offer Config",
            "create": "Create",
            "replicate": "Replicate",
            "analyze": "Analyze Script",
            "visual": "Video Breakdown",
            "upload": "Upload Video",
            "uploaded": "Video Uploaded",
            "link": "Add Link",
            "link_added": "Link Added",
            "images": "Product Images",
            "images_open": "Product Images Open",
            "run": "Start AI Rebuilder",
            "video_url": "Video URL",
            "upload_video": "Upload Short Video File",
            "upload_images": "Upload Your Product Images",
            "scene": "Shooting Scene",
            "target_seconds": "Target Seconds",
            "script_label": "Video Script / Product Info",
            "create_placeholder": "Enter product selling points...",
            "replicate_placeholder": "Enter the video description or voiceover you want to replicate...",
            "analyze_placeholder": "Paste the original script you want to analyze...",
            "visual_placeholder": "Describe the camera logic to keep and your product/package/scene requirements...",
            "extracting": "Extracting frames and camera rhythm from uploaded video...",
            "url_processing": "Analyzing video URL metadata and audio track...",
            "thinking": "AI is breaking down the video and generating the storyboard...",
            "keyframes": "Uploaded Video Keyframes",
            "keyframes_caption": "Reference video keyframes",
            "storyboard": "Video Storyboard",
            "assistant": "AI Script Design Assistant",
            "chat_placeholder": "Ask me any question related to this video...",
            "system_status": "System Status",
            "generated_msg": "Here is the video structure breakdown and storyboard for **{product}**.\n\n{status}\n\nYou can ask me to modify any part of it below.",
            "no_video": "No uploaded reference video found. Please upload a video for visual breakdown; generating from text/product images for now.",
            "video_error": "Uploaded video analysis error: {error}. Rebuilding using text and product images only.",
            "audio_unsupported": "Speech-to-text API (whisper-1) is not supported on this API key proxy. Rebuilding using video title and description metadata instead.",
            "audio_missing": "Could not download video audio. Rebuilding using video title and description metadata instead.",
            "url_error": "Video processing error: {error}. Rebuilding using pasted text details instead.",
            "output_language": "English",
        },
        "Nigerian Pidgin": {
            "center_title": "Analyze, Copy or Make Viral Videos",
            "center_desc": "Upload reference video, product pictures, or product details. AI go break down the camera style and make storyboard for your own product.",
            "offer_config": "Product & Offer Setup",
            "create": "Create New",
            "replicate": "Copy Style",
            "analyze": "Analyze Script",
            "visual": "Video Breakdown",
            "upload": "Upload Video",
            "uploaded": "Video Don Upload",
            "link": "Add Link",
            "link_added": "Link Don Add",
            "images": "Product Pictures",
            "images_open": "Product Pictures Open",
            "run": "Start AI Rebuilder",
            "video_url": "Video Link",
            "upload_video": "Upload Short Video File",
            "upload_images": "Upload Your Product Pictures",
            "scene": "Shooting Scene",
            "target_seconds": "Target Seconds",
            "script_label": "Video Script / Product Info",
            "create_placeholder": "Put your product selling points here...",
            "replicate_placeholder": "Put the video description or voiceover wey you wan copy...",
            "analyze_placeholder": "Paste the original script wey you wan analyze...",
            "visual_placeholder": "Tell AI the camera style to keep and your product/package/scene needs...",
            "extracting": "AI dey extract frames and camera rhythm from uploaded video...",
            "url_processing": "AI dey check video link metadata and audio track...",
            "thinking": "AI dey break down the video and build storyboard...",
            "keyframes": "Uploaded Video Keyframes",
            "keyframes_caption": "Reference video keyframes",
            "storyboard": "Video Storyboard",
            "assistant": "AI Script Design Assistant",
            "chat_placeholder": "Ask me any question about dis video...",
            "system_status": "System Status",
            "generated_msg": "Here na the video breakdown and storyboard for **{product}**.\n\n{status}\n\nYou fit ask me to change any part below.",
            "no_video": "No reference video upload yet. Upload video make AI fit break am down; for now AI go use text and product pictures.",
            "video_error": "Uploaded video analysis get issue: {error}. AI go use text and product pictures only.",
            "audio_unsupported": "This API key proxy no support speech-to-text (whisper-1). AI go use video title and description metadata instead.",
            "audio_missing": "Audio download no work. AI go use video title and description metadata instead.",
            "url_error": "Video processing get issue: {error}. AI go use the text wey you paste instead.",
            "output_language": "Nigerian Pidgin",
        },
    }
    t4_ui = T4_UI[sys_lang]
    t4_center_title = t4_ui["center_title"]
    t4_center_desc = t4_ui["center_desc"]
    t4_label_upload = t4_ui["upload"]
    t4_label_link = t4_ui["link"]
    t4_label_run = t4_ui["run"]
    t4_chat_placeholder = t4_ui["chat_placeholder"]

    # Check which view to display (Console vs Analysis)
    # 1. Title Header (Center aligned)
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 24px;">
        <h1 style="font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {t4_center_title}
        </h1>
        <p style="color: #94a3b8; font-size: 1rem; max-width: 600px; margin: 0 auto;">
            {t4_center_desc}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 8px 0 24px 0; border-color: rgba(255, 255, 255, 0.15);'/>", unsafe_allow_html=True)
    
    # 2. Input Console Container
    with st.container():
        # Product & Offer Config for Tab 4 (Independent from Tab 3)
        st.markdown(f'<div style="margin-bottom: 12px; font-weight: 600; color: #f8fafc;">📦 {t4_ui["offer_config"]}</div>', unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            t4_prod = st.text_input(L["t3_active_prod"], value=st.session_state.t4_prod, key="t4_prod_input")
            st.session_state.t4_prod = t4_prod
        with sc2:
            t4_price = st.number_input(L["t3_active_price"], min_value=1, value=st.session_state.t4_price, key="t4_price_input")
            st.session_state.t4_price = t4_price
        with sc3:
            t4_moq = st.number_input(L["t3_active_moq"], min_value=1, value=st.session_state.t4_moq, key="t4_moq_input")
            st.session_state.t4_moq = t4_moq
        st.markdown("<hr style='margin: 16px 0; border-color: rgba(255, 255, 255, 0.1);'/>", unsafe_allow_html=True)
        
        # Mode Pills Selector
        p_col1, p_col2, p_col3, p_col4, p_col_spacer = st.columns([1.2, 1.2, 1.2, 1.45, 2.4])
        with p_col1:
            active_create = (st.session_state.t4_mode == "create")
            if st.button("🎨 " + t4_ui["create"], type="primary" if active_create else "secondary", use_container_width=True, key="t4_pill_create"):
                st.session_state.t4_mode = "create"
                st.session_state.t4_video_analysis = None
                st.session_state.t4_video_montage_b64 = ""
                st.session_state.t4_input_create = T4_DEFAULT_INPUTS[sys_lang]["create"]
                st.session_state.t4_main_input = st.session_state.t4_input_create
                st.rerun()
        with p_col2:
            active_replicate = (st.session_state.t4_mode == "replicate")
            if st.button("🔄 " + t4_ui["replicate"], type="primary" if active_replicate else "secondary", use_container_width=True, key="t4_pill_replicate"):
                st.session_state.t4_mode = "replicate"
                st.session_state.t4_video_analysis = None
                st.session_state.t4_video_montage_b64 = ""
                st.session_state.t4_input_replicate = T4_DEFAULT_INPUTS[sys_lang]["replicate"]
                st.session_state.t4_main_input = st.session_state.t4_input_replicate
                st.rerun()
        with p_col3:
            active_analyze = (st.session_state.t4_mode == "analyze")
            if st.button("📊 " + t4_ui["analyze"], type="primary" if active_analyze else "secondary", use_container_width=True, key="t4_pill_analyze"):
                st.session_state.t4_mode = "analyze"
                st.session_state.t4_video_analysis = None
                st.session_state.t4_video_montage_b64 = ""
                st.session_state.t4_input_analyze = T4_DEFAULT_INPUTS[sys_lang]["analyze"]
                st.session_state.t4_main_input = st.session_state.t4_input_analyze
                st.rerun()
        with p_col4:
            active_visual = (st.session_state.t4_mode == "visual_replicate")
            if st.button("🎥 " + t4_ui["visual"], type="primary" if active_visual else "secondary", use_container_width=True, key="t4_pill_visual_replicate"):
                st.session_state.t4_mode = "visual_replicate"
                st.session_state.t4_input_visual_replicate = T4_DEFAULT_INPUTS[sys_lang]["visual_replicate"]
                st.session_state.t4_main_input = st.session_state.t4_input_visual_replicate
                st.session_state.t4_show_upload = True
                st.session_state.t4_show_product_images = True
                st.rerun()
        
        # Main Input Text Area
        if st.session_state.t4_mode == "analyze":
            ta_placeholder = t4_ui["analyze_placeholder"]
            ta_value_default = st.session_state.t4_input_analyze
        elif st.session_state.t4_mode == "replicate":
            ta_placeholder = t4_ui["replicate_placeholder"]
            ta_value_default = st.session_state.t4_input_replicate
        elif st.session_state.t4_mode == "visual_replicate":
            ta_placeholder = t4_ui["visual_placeholder"]
            ta_value_default = st.session_state.get("t4_input_visual_replicate", "")
        else:
            ta_placeholder = t4_ui["create_placeholder"]
            ta_value_default = st.session_state.t4_input_create
            
        t4_user_input = st.text_area(
            label=t4_ui["script_label"],
            placeholder=ta_placeholder,
            value=ta_value_default,
            height=180,
            key="t4_main_input",
            label_visibility="collapsed"
        )
        
        # Save user edit back to respective mode input state
        if st.session_state.t4_mode == "analyze":
            st.session_state.t4_input_analyze = t4_user_input
        elif st.session_state.t4_mode == "replicate":
            st.session_state.t4_input_replicate = t4_user_input
        elif st.session_state.t4_mode == "visual_replicate":
            st.session_state.t4_input_visual_replicate = t4_user_input
        else:
            st.session_state.t4_input_create = t4_user_input
        
        # Action Row (Add Link, Upload, Run)
        act_col1, act_col2, act_col_img, act_col3 = st.columns([1.2, 1.2, 1.4, 2])
        with act_col1:
            btn_link_label = "🔗 " + (t4_ui["link_added"] if st.session_state.t4_show_link else t4_label_link)
            if st.button(btn_link_label, use_container_width=True, key="t4_btn_toggle_link"):
                st.session_state.t4_show_link = not st.session_state.t4_show_link
                st.rerun()
        with act_col2:
            btn_upload_label = "📤 " + (t4_ui["uploaded"] if st.session_state.t4_show_upload else t4_label_upload)
            if st.button(btn_upload_label, use_container_width=True, key="t4_btn_toggle_upload"):
                st.session_state.t4_show_upload = not st.session_state.t4_show_upload
                st.rerun()
        with act_col_img:
            btn_img_label = "🖼️ " + (t4_ui["images_open"] if st.session_state.t4_show_product_images else t4_ui["images"])
            if st.button(btn_img_label, use_container_width=True, key="t4_btn_toggle_product_images"):
                st.session_state.t4_show_product_images = not st.session_state.t4_show_product_images
                st.rerun()
        with act_col3:
            run_rebuild = st.button("🚀 " + t4_label_run, type="primary", use_container_width=True, key="t4_btn_rebuild_submit")
            
        # Dynamic Inputs below row
        if st.session_state.t4_show_link:
            st.text_input(
                "🔗 " + t4_ui["video_url"], 
                value="", 
                key="t4_link_in_dyn"
            )
        if st.session_state.t4_show_upload:
            t4_uploaded_video = st.file_uploader(
                "📤 " + t4_ui["upload_video"], 
                type=["mp4", "mov", "avi"], 
                key="t4_upload_in_dyn"
            )
        else:
            t4_uploaded_video = None
        if st.session_state.t4_mode == "visual_replicate":
            vc1, vc2 = st.columns([1.4, 1])
            with vc1:
                t4_scene = st.text_input(
                    "🎬 " + t4_ui["scene"],
                    value=st.session_state.t4_scene,
                    key="t4_scene_input"
                )
                st.session_state.t4_scene = t4_scene
            with vc2:
                t4_target_seconds = st.number_input(
                    "⏱️ " + t4_ui["target_seconds"],
                    min_value=3,
                    max_value=120,
                    value=int(st.session_state.t4_target_seconds),
                    key="t4_target_seconds_input"
                )
                st.session_state.t4_target_seconds = int(t4_target_seconds)
        if st.session_state.t4_show_product_images:
            t4_product_images = st.file_uploader(
                "🖼️ " + t4_ui["upload_images"],
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key="t4_product_images_dyn"
            )
        else:
            t4_product_images = []
        
    # Rebuild submit logic
    if run_rebuild:
        video_title = f"{st.session_state.t4_mode.upper()} - {st.session_state.t4_prod}"
        st.session_state.t4_video_title = video_title
        
        video_url = st.session_state.get("t4_link_in_dyn", "").strip()
        extracted_script_context = t4_user_input
        status_info = ""
        vision_images = []
        product_image_context = ""
        uploaded_video_obj = st.session_state.get("t4_upload_in_dyn")
        product_image_objs = st.session_state.get("t4_product_images_dyn") or []
        if product_image_objs:
            product_names = ", ".join([img.name for img in product_image_objs])
            product_image_context = f"\nUploaded Product Images: {len(product_image_objs)} file(s): {product_names}\nUse these images to identify the user's real product/menu items, plating, colors, materials, and visual selling points.\n"
            vision_images.extend(product_image_objs[:5])
        
        if st.session_state.t4_mode == "visual_replicate" and uploaded_video_obj:
            with st.spinner(t4_ui["extracting"]):
                try:
                    import video_processor
                    local_video_path = video_processor.save_uploaded_video(uploaded_video_obj)
                    visual_analysis = video_processor.analyze_local_video(local_video_path)
                    st.session_state.t4_video_analysis = visual_analysis
                    montage_img = visual_analysis.get("montage_image")
                    st.session_state.t4_video_montage_b64 = get_base64_image(montage_img)
                    vision_images.insert(0, montage_img)
                    extracted_script_context = f"{t4_user_input}\n\n{visual_analysis.get('prompt_context', '')}{product_image_context}"
                    status_info = f"Uploaded video analyzed: {visual_analysis.get('duration')}s, {visual_analysis.get('estimated_shots')} estimated shots, {visual_analysis.get('rhythm')} rhythm."
                except Exception as proc_err:
                    status_info = t4_ui["video_error"].format(error=proc_err)
                    extracted_script_context = f"{t4_user_input}\n{product_image_context}"
        elif st.session_state.t4_mode == "visual_replicate":
            status_info = t4_ui["no_video"]
            extracted_script_context = f"{t4_user_input}\n{product_image_context}"
        
        if st.session_state.t4_show_link and video_url:
            with st.spinner(t4_ui["url_processing"]):
                try:
                    import video_processor
                    
                    # 1. Try metadata extraction
                    meta = video_processor.get_video_metadata(video_url)
                    meta_text = ""
                    if meta:
                        meta_text = f"Video Title: {meta.get('title')}\nDescription: {meta.get('description')}\nTags: {', '.join(meta.get('tags', []))}\nDuration: {meta.get('duration')}s"
                    
                    # 2. Try raw audio track extraction
                    audio_path = video_processor.extract_audio_from_url(video_url)
                    transcript = None
                    if audio_path:
                        try:
                             # Try transcription via Whisper API
                            transcript = video_processor.transcribe_audio(audio_path, openai_api_key, openai_base_url)
                            # Clean up downloaded file
                            import os
                            if os.path.exists(audio_path):
                                os.remove(audio_path)
                        except Exception as whisper_err:
                            status_info = t4_ui["audio_unsupported"]
                    else:
                        status_info = t4_ui["audio_missing"]
                    
                    # Combine context
                    if transcript:
                        extracted_script_context = f"Video Transcript:\n{transcript}\n\nVideo Metadata:\n{meta_text}"
                    elif meta_text:
                        extracted_script_context = f"Video Metadata (No Transcript):\n{meta_text}\n\nAdditional Input Context:\n{t4_user_input}"
                except Exception as proc_err:
                    status_info = t4_ui["url_error"].format(error=proc_err)
        
        if st.session_state.t4_mode == "visual_replicate":
            visual_format = {
                "简体中文": """# 1. 原视频运镜拆解
- 总时长、节奏、镜头数量估算
- 镜头语言：低机位/俯拍/横移/前推/后拉/硬切等
- 画面逻辑：主体如何出现、如何分批上桌、如何制造食欲或购买欲

# 2. 可迁移拍摄逻辑
用 5-8 条说明哪些部分可以迁移到新产品，哪些部分不要复制。

# 3. 定制拍摄分镜脚本
用 Markdown 表格输出，必须适配用户目标秒数。
表格列：
| 时间 | 画面内容 | 运镜方式 | 动作/上菜节奏 | 拍摄重点 |

# 4. 可直接复制给视频 Agent 的提示词
写成一个完整 prompt，包含画幅、时长、场景、产品、分批出现顺序、运镜、剪辑节奏、禁止项。""",
                "English": """# 1. Reference Video Camera Breakdown
- Total duration, rhythm, estimated shot count
- Camera language: low angle, overhead shot, side sweep, push-in, pull-back, hard cuts
- Visual logic: how the subject appears, how items enter in batches, how desire is created

# 2. Transferable Shooting Logic
Use 5-8 bullets to explain what should transfer to the new product and what must not be copied.

# 3. Custom Shooting Storyboard
Use a Markdown table and match the user's target duration.
Table columns:
| Time | Visual Content | Camera Movement | Action / Serving Rhythm | Shooting Focus |

# 4. Copy-Ready Prompt for Video Agent
Write one complete prompt including aspect ratio, duration, scene, product, batch-by-batch order, camera movement, cut rhythm, and negative instructions.""",
                "Nigerian Pidgin": """# 1. Reference Video Camera Breakdown
- Total time, rhythm, estimated shot count
- Camera style: low angle, top shot, side sweep, push-in, pull-back, hard cuts
- Visual logic: how product enter, how items show batch by batch, how e take make person want am

# 2. Shooting Logic Wey Fit Transfer
Use 5-8 bullets explain wetin fit transfer to the new product and wetin no suppose copy.

# 3. Custom Shooting Storyboard
Use Markdown table and match the target seconds.
Table columns:
| Time | Visual Content | Camera Movement | Action / Serving Rhythm | Shooting Focus |

# 4. Prompt Wey Fit Copy Give Video Agent
Write one complete prompt with aspect ratio, duration, scene, product, batch-by-batch order, camera movement, cut rhythm, and things wey no suppose show.""",
            }[sys_lang]
            bilingual_visual_format = """For BOTH language versions, use the same structure:

Chinese version structure:
# 1. 原视频运镜拆解
# 2. 可迁移拍摄逻辑
# 3. 定制拍摄分镜脚本
| 时间 | 画面内容 | 运镜方式 | 动作/上菜节奏 | 拍摄重点 |
# 4. 可直接复制给视频 Agent 的提示词

English version structure:
# 1. Reference Video Camera Breakdown
# 2. Transferable Shooting Logic
# 3. Custom Shooting Storyboard
| Time | Visual Content | Camera Movement | Action / Serving Rhythm | Shooting Focus |
# 4. Copy-Ready Prompt for Video Agent"""
            system_prompt_script = f"""You are a senior short-video director and visual storyboard strategist.
You specialize in decomposing reference videos into reusable filming logic, then adapting that logic to a user's own products, images, scene, and target duration.

Your job:
1. Analyze the uploaded reference video evidence: keyframe montage, duration, cut timestamps, camera rhythm, composition, staging, object-entry timing, hand/action rhythm, and ending structure.
2. Do NOT copy the original product, location, brand, UI, subtitle overlay, or exact subject. Copy only the reusable camera movement and editing logic.
3. Use the user's uploaded product images and product details to create a custom shooting storyboard.
4. Generate BOTH Chinese and English in ONE response.
5. Keep the result practical enough for a video generation agent or a real camera operator.

CRITICAL OUTPUT FORMAT:
- Start the Chinese version with exactly: [[ZH]]
- Start the English version with exactly: [[EN]]
- Do not put any text before [[ZH]].
- Do not omit either version.
- The two versions must contain the same shot logic, timing, and structure.

Required structure:
{bilingual_visual_format}
"""
            user_prompt_script = f"""
Reference Video / User Instruction:
{extracted_script_context}

User's Target Product and Scene:
- Product/Menu Name: {st.session_state.t4_prod}
- Target Duration: {st.session_state.t4_target_seconds} seconds
- Target Scene: {st.session_state.t4_scene}
- Price/Offer: {st.session_state.t4_price} NGN
- MOQ/Quantity: {st.session_state.t4_moq}
- Contact: {watermark_phone}

Please generate a custom bilingual shooting breakdown that transfers the reference video's camera movement logic to the user's own product/images.
"""
        else:
            system_prompt_script = f"""You are a highly talented West African video director and TikTok/Reels advertising copywriter.
Your task is to take a short video transcript, text description, or metadata details, analyze its viral hook structure, and rewrite it into a localized high-converting short video script for the West African (Nigerian) market.

CRITICAL CONSTRAINTS:
1. Generate BOTH Chinese and English in ONE response.
2. If the target product specifies 0 main images or no assets, make sure the visual descriptions and script flow accommodate this safely.
3. Start the Chinese version with exactly: [[ZH]]
4. Start the English version with exactly: [[EN]]
5. Do not put any text before [[ZH]]. Do not omit either version.

For BOTH language versions, use this structure:

# Part 1 / 第 1 部分: Viral Structure Analysis / 爆款结构分析
- **Hook Strategy (First 3s)**: Explain the hook design and why it grabs attention.
- **Core Narrative Structure (Problem -> Agitation -> Solution -> CTA)**: Breakdown the narrative sequence.
- **Emotional Triggers**: List the primary psychological and emotional triggers.

# Part 2 / 第 2 部分: Localized Shooting Storyboard / 本地化拍摄分镜
Provide a markdown table detailing the visual camera shots (Visual & Camera), the English spoken dialogue (Dialogue / Audio) in local high-energy Nigerian English tone, and action directions for the actor (Action & Tone).

Format the storyboard strictly as a Markdown table:
| Section | Visual & Camera | Dialogue / Audio | Action & Tone |
| :--- | :--- | :--- | :--- |
| **Hook (0-3s)** | ... | ... | ... |
| **Body (4-15s)** | ... | ... | ... |
| **CTA (16-30s)** | ... | ... | ... |
"""

            user_prompt_script = f"""
Original Video Script/Details:
{extracted_script_context}

Target Wholesale Product details:
- Product Name: {st.session_state.t4_prod}
- Wholesale Clearance Price: {st.session_state.t4_price} NGN
- MOQ: {st.session_state.t4_moq} units
- Pickup Warehouse: {lagos_address}
- WhatsApp Contact: {watermark_phone}

Please write the localized bilingual script storyboard based on the target product details.
"""
        with st.spinner(t4_ui["thinking"]):
            if st.session_state.t4_mode == "visual_replicate":
                response_script = call_llm_with_images(
                    system_prompt_script,
                    user_prompt_script,
                    vision_images,
                    lambda: f"""[[ZH]]
# 1. 原视频运镜拆解
- 节奏：短视频快切，重点是贴近主体、分批出现、最后满桌展示。
- 镜头：低机位贴桌前推、横向扫桌、俯拍下压、末尾后拉展示完整产品。

# 2. 可迁移拍摄逻辑
- 保留手持轻微晃动和硬切节奏。
- 保留产品从画外分批进入桌面的方式。
- 不复制原视频的产品、场景和平台 UI。

# 3. 定制拍摄分镜脚本
| 时间 | 画面内容 | 运镜方式 | 动作/上菜节奏 | 拍摄重点 |
| :--- | :--- | :--- | :--- | :--- |
| 0-2s | 空桌或半空桌，先放入主饮品/主产品 | 低机位贴桌前推 | 服务员手从画外放入第一批产品 | 建立场景和第一眼吸引 |
| 2-4s | 第二批产品补充到桌面 | 横向扫桌 | 从左到右依次上菜 | 强调“越来越丰富” |
| 4-7s | 主菜/核心套餐靠近镜头 | 俯拍下压再轻推 | 手部摆盘、转盘或夹起 | 展示质感和卖点 |
| 7-{st.session_state.t4_target_seconds}s | 满桌最终展示 | 轻微后拉定格 | 所有产品完整出现 | 给 agent 一个完整收尾画面 |

# 4. 可直接复制给视频 Agent 的提示词
生成一个 {st.session_state.t4_target_seconds} 秒竖屏短视频，场景是 {st.session_state.t4_scene}，产品是 {st.session_state.t4_prod}。使用手机手持美食/产品短视频运镜：低机位贴桌、前推、横扫、俯拍下压、结尾后拉满桌展示。产品分批从画外放入桌面，直接硬切，突出真实感和产品质感。不要复制参考视频原产品，不要出现平台 UI。

[[EN]]
# 1. Reference Video Camera Breakdown
- Rhythm: short-video cuts, close to the subject, batch-by-batch entry, final full-table/product reveal.
- Camera: low table-level push-in, side sweep, overhead press-in, final pull-back.

# 2. Transferable Shooting Logic
- Keep the handheld micro-shake and hard-cut rhythm.
- Keep the way products enter the frame from outside in batches.
- Do not copy the original product, original scene, or platform UI.

# 3. Custom Shooting Storyboard
| Time | Visual Content | Camera Movement | Action / Serving Rhythm | Shooting Focus |
| :--- | :--- | :--- | :--- | :--- |
| 0-2s | Empty or half-empty table, first main drink/product enters | Low table-level push-in | Hand places the first batch into frame | Establish scene and first hook |
| 2-4s | Second batch of products fills the table | Side sweep | Items enter from left to right | Show the table becoming richer |
| 4-7s | Core product/package moves close to camera | Overhead press-in, slight push | Hands adjust, plate, rotate, or lift product | Show texture and selling point |
| 7-{st.session_state.t4_target_seconds}s | Final full-table/product reveal | Gentle pull-back and hold | All products are visible | Give the agent a complete closing shot |

# 4. Copy-Ready Prompt for Video Agent
Generate a {st.session_state.t4_target_seconds}-second vertical video in this scene: {st.session_state.t4_scene}. Product: {st.session_state.t4_prod}. Use handheld food/product short-video camera language: low table-level angle, push-in, side sweep, overhead press-in, final pull-back full reveal. Products enter the table in batches from outside the frame. Use direct hard cuts, real texture, and strong product presence. Do not copy the reference video's original product or platform UI."""
                )
            else:
                response_script = call_llm(
                    system_prompt_script,
                    user_prompt_script,
                    lambda: get_mock_video_script(t4_user_input, st.session_state.t4_prod, st.session_state.t4_price, watermark_phone, lagos_address)
                )
            st.session_state.rebuilt_script = response_script
            zh_script, en_script = split_bilingual_script(response_script)
            if zh_script and not en_script:
                en_script = call_llm(
                    "Translate this markdown storyboard into English. Preserve all tables, timing, product names, prices, and numbers. Output only the translated content.",
                    zh_script,
                    lambda: ""
                )
            if en_script and not zh_script:
                zh_script = call_llm(
                    "Translate this markdown storyboard into Simplified Chinese. Preserve all tables, timing, product names, prices, and numbers. Output only the translated content.",
                    en_script,
                    lambda: ""
                )
            st.session_state.rebuilt_script_zh = zh_script
            st.session_state.rebuilt_script_en = en_script
            st.session_state.rebuilt_script = zh_script or en_script or response_script
            st.session_state.t4_output_lang = "bilingual"
            
            status_line = f"ℹ️ *{t4_ui['system_status']}: {status_info}*" if status_info else ""
            assistant_content = t4_ui["generated_msg"].format(product=st.session_state.t4_prod, status=status_line)
            
            st.session_state.t4_chat_history = [
                {
                    "role": "assistant",
                    "content": assistant_content
                }
            ]
            st.rerun()

    # Show Output Results directly below on the same page
    if st.session_state.rebuilt_script or st.session_state.rebuilt_script_zh or st.session_state.rebuilt_script_en:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # 2. Localized Storyboard Script Table
        if st.session_state.get("t4_video_montage_b64"):
            st.markdown("### 🧩 " + t4_ui["keyframes"], unsafe_allow_html=True)
            st.image(st.session_state.t4_video_montage_b64, caption=t4_ui["keyframes_caption"])
            visual_analysis = st.session_state.get("t4_video_analysis") or {}
            if visual_analysis:
                st.caption(
                    f"Duration: {visual_analysis.get('duration')}s | "
                    f"Estimated shots: {visual_analysis.get('estimated_shots')} | "
                    f"Rhythm: {visual_analysis.get('rhythm')} | "
                    f"Avg shot: {visual_analysis.get('avg_shot_len')}s"
                )
            st.markdown("---")
        
        st.markdown("### 🎬 " + t4_ui["storyboard"], unsafe_allow_html=True)
        zh_tab, en_tab = st.tabs(["中文", "English"])
        with zh_tab:
            st.markdown(st.session_state.rebuilt_script_zh or st.session_state.rebuilt_script or "暂无中文版本")
        with en_tab:
            st.markdown(st.session_state.rebuilt_script_en or "No English version was parsed from the AI response.")
        
        # 3. Chat Feed Area
        st.markdown("---")
        st.markdown("### 💬 " + t4_ui["assistant"], unsafe_allow_html=True)
        
        for msg in st.session_state.t4_chat_history:
            bubble_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
            align_style = "display: flex; flex-direction: column;"
            st.markdown(f"""
            <div style="{align_style}">
                <div class="chat-bubble {bubble_class}">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # 4. Interactive Chat Input
        user_query = st.chat_input(t4_chat_placeholder)
        if user_query:
            st.session_state.t4_chat_history.append({"role": "user", "content": user_query})
            
            followup_system_prompt = """You are a highly talented West African video director and copywriter.
The user is working with you to adjust or translate a short video storyboard.
The current storyboard script table is:
{current_script}

Your goal:
1. If the user wants to adjust the script (e.g. change language to Pidgin, change product, lower price, add hook, change CTA, etc.), update the markdown script table and return it at the BEGINNING of your response.
2. Provide a short, energetic, friendly West African director explanation after the table.
3. If they just ask questions, answer them in an energetic local director's voice.
4. Output EVERYTHING in {output_language}. Do not mix languages.
Always keep the script table strictly in markdown format."""

            followup_user_prompt = f"""
Current Script:
{st.session_state.rebuilt_script}

User's Request: {user_query}
"""
            with st.spinner(t4_ui["thinking"]):
                response = call_llm(
                    followup_system_prompt.format(current_script=st.session_state.rebuilt_script, output_language=t4_ui["output_language"]),
                    followup_user_prompt,
                    lambda: "Here is the updated script table based on your instruction:\n\n" + st.session_state.rebuilt_script + f"\n\nDirector: I have updated the script for you. Let's make it hit double sales!"
                )
                
                # Check if there is an updated table inside response
                explanation = response
                if "|" in response and "---" in response:
                    lines = response.split("\n")
                    table_lines = []
                    non_table_lines = []
                    in_table = False
                    for line in lines:
                        if "|" in line:
                            table_lines.append(line)
                            in_table = True
                        else:
                            if in_table and line.strip() == "":
                                continue
                            non_table_lines.append(line)
                    
                    if len(table_lines) > 2:
                        st.session_state.rebuilt_script = "\n".join(table_lines)
                        st.session_state.rebuilt_script_zh = st.session_state.rebuilt_script
                        st.session_state.t4_output_lang = sys_lang
                        explanation = "\n".join(non_table_lines).strip()
                        
                st.session_state.t4_chat_history.append({"role": "assistant", "content": explanation})
                st.rerun()

# ---------------------------------------------------------
# Tab 5: 社媒投流辅助 (Ads Pilot)
# ---------------------------------------------------------
if st.session_state.current_page == "ads":
    render_dashboard_header(L['t5_header'], L['t5_desc'], "Console // Social Ads Pilot")
    
    col_ad1, col_ad2 = st.columns([1, 1])
    
    with col_ad1:
        with st.container(border=True):
            st.markdown(f'### <i class="fa-solid fa-chart-pie"></i> {L["t5_input_header"]}', unsafe_allow_html=True)
            
            ad_channel = st.multiselect(L["t5_channel_label"], ["Meta Ads (FB/IG)", "TikTok Ads"], default=["Meta Ads (FB/IG)"], key="t5_channels_in")
            
            # Budget translations
            if sys_lang == "简体中文":
                budgets = ["小额测试 (10 - 50 USD / 天)", "中等爆单 (50 - 200 USD / 天)", "大批量压制 (200+ USD / 天)"]
            elif sys_lang == "English":
                budgets = ["Small test (10 - 50 USD / day)", "Medium scaling (50 - 200 USD / day)", "Mass scale (200+ USD / day)"]
            else: # Pidgin
                budgets = ["Small check (10 - 50 USD / day)", "Big scaling (50 - 200 USD / day)", "Heavy container scale (200+ USD / day)"]
                
            budget_level = st.selectbox(L["t5_budget_label"], budgets, index=0)
            
            ad_generate_btn = st.button(L["t5_btn"], type="primary")
            
            # Nigerian marketing tips translated
            if sys_lang == "简体中文":
                st.markdown("""
                ##### <i class='fa-solid fa-lightbulb'></i> 尼日利亚投流核心知识:
                - **Jiji 强关联**: 尼日利亚本土的 Jiji.ng 类似于闲鱼，其受众群对“价格敏感的批发杂货”转化率极高。
                - **互动买家 (Engaged Shoppers)**: Meta 广告中这个行为限定标签可以过滤掉大量没有信用卡或没有消费力、只是看热闹的人。
                - **直接 WhatsApp 转化**: 在尼日利亚，使用独立站表单转化率极低，直接跳转 WhatsApp 私域聊天是公认的爆单路径。
                """, unsafe_allow_html=True)
            elif sys_lang == "English":
                st.markdown("""
                ##### <i class='fa-solid fa-lightbulb'></i> Nigeria Campaign Knowledge:
                - **Jiji.ng Association**: Jiji.ng is Nigeria's biggest classification site. Wholesalers here are extremely sensitive to price drops.
                - **Engaged Shoppers**: This Meta behavior constraint filters out window shoppers who do not buy online.
                - **Direct WhatsApp Funnel**: Conversion via web forms is low in West Africa. Send traffic to WhatsApp chat for instant conversions.
                """, unsafe_allow_html=True)
            else: # Pidgin
                st.markdown("""
                ##### <i class='fa-solid fa-lightbulb'></i> Naija Ads secrets:
                - **Jiji connection**: Jiji.ng na the biggest market place. People looking for low price go find you sharp-sharp.
                - **Engaged Shoppers**: Must click this setting for Facebook ads make you filter out window shoppers.
                - **Direct WhatsApp link**: Don't use website forms, local buyers don't fill forms. Send them straight to WhatsApp.
                """, unsafe_allow_html=True)

            # Lagos Reseller Pricing & Margin Calculator
            st.markdown("---")
            with st.expander("📊 Lagos Reseller Pricing & Margin Calculator" if sys_lang != "简体中文" else "📊 尼日利亚分销商清仓利润率测算工具", expanded=False):
                st.markdown("Calculate break-even and wholesale profit margins to convince resellers on Jiji and Balogun market." if sys_lang == "English" else "Calculate wholesale profit margins to show resellers." if sys_lang == "Nigerian Pidgin" else "测算清仓保本点以及 Balogun 等线下市场的渠道利润，用真实数据说服采购商。")
                
                calc_price = st.number_input("Clearance Price (NGN)", min_value=1, value=active_price, step=500, key="calc_price_in")
                calc_moq = st.number_input("Reseller MOQ", min_value=1, value=active_moq, step=10, key="calc_moq_in")
                
                tr_price = st.number_input("Est. Lagos Retail Price (NGN)", min_value=1, value=int(calc_price * 1.5), step=500, key="tr_price_in")
                
                # Math
                unit_markup = tr_price - calc_price
                margin_pct = (unit_markup / calc_price) * 100 if calc_price > 0 else 0
                total_moq_cost = calc_price * calc_moq
                total_moq_retail = tr_price * calc_moq
                moq_profit = total_moq_retail - total_moq_cost
                
                # Visual output
                st.markdown(f"""
                <div style="background-color:rgba(0, 242, 254, 0.05); border:1px solid rgba(0, 242, 254, 0.2); padding:16px; border-radius:12px; margin-top:12px; font-family:'Inter', sans-serif;">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                        <div>
                            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase;">Reseller Profit / Unit</span><br/>
                            <span style="font-size:1.1rem; font-weight:800; color:#00F2FE;">{unit_markup:,} NGN</span>
                        </div>
                        <div>
                            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase;">Reseller ROI %</span><br/>
                            <span style="font-size:1.1rem; font-weight:800; color:#7C3AED;">+{margin_pct:.1f}%</span>
                        </div>
                        <div>
                            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase;">Batch Buy Cost (MOQ)</span><br/>
                            <span style="font-size:1rem; font-weight:700; color:#FFFFFF;">{total_moq_cost:,} NGN</span>
                        </div>
                        <div>
                            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase;">Batch Est. Profit</span><br/>
                            <span style="font-size:1rem; font-weight:700; color:#22c55e;">+{moq_profit:,} NGN</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.info("💡 Pro-Tip: You can use this profit margin calculation in your marketing copies to attract more wholesale resellers. Tell them: 'Buy a batch of chairs for 625,000 NGN, sell them in Ikeja for 937,500 NGN, make 312,500 NGN sharp profit!'" if sys_lang == "English" else "💡 Talk true: You fit add dis margin inside your ads copies. Tell traders: 'Buy MOQ container batch for 625k NGN, sell them in Lagos market for 937k NGN, make 312k sharp profit!'" if sys_lang == "Nigerian Pidgin" else "💡 话术诀窍：您可以直接把利润率写在文案中吸引分销商。例如：‘进一箱货成本 625,000 NGN，在拉各斯市场上能卖 937,500 NGN，立赚 312,500 NGN 纯利！’")
        
    with col_ad2:
        with st.container(border=True):
            st.markdown(f'### <i class="fa-solid fa-bullseye"></i> {L["t5_out_header"]}', unsafe_allow_html=True)
            
            if ad_generate_btn:
                system_prompt_ad = """You are an expert Meta and TikTok ad performance marketer specialized in the sub-Saharan African market.
Your task is to generate Meta/TikTok targeting configurations, 3 high-converting A/B testing ad copy variations in English, and a data-driven diagnosis guide for the specified clearance product.
Keep the outputs professional, structured with markdown tables and bullet points. Output must be in English for the ad copies, and Chinese for targeting instructions."""

                user_prompt_ad = f"""
Product: {active_prod}
Category: {prod_category}
Price: {active_price} NGN
MOQ: {active_moq} units
WhatsApp Contact: {watermark_phone}
Target Budget Level: {budget_level}
Selected Channels: {', '.join(ad_channel)}
"""
                
                with st.spinner("AI is calculating performance plans..." if sys_lang != "简体中文" else "AI 正在根据尼日利亚大盘投流数据，规划您的广告方案..."):
                    response_ad = call_llm(
                        system_prompt_ad,
                        user_prompt_ad,
                        lambda: get_mock_ad_campaign_guide(active_prod, prod_category, active_price, active_moq, watermark_phone)
                    )
                    st.session_state.campaign_plan = response_ad
                    
            if st.session_state.campaign_plan:
                st.markdown(st.session_state.campaign_plan)
            else:
                st.info(L["t5_info"])

# ---------------------------------------------------------
# Tab 6: 培训教材与 SOP 交付中心 (SOP Manual)
# ---------------------------------------------------------
if st.session_state.current_page == "training":
    render_dashboard_header(L['t6_header'], L['t6_desc'], "Console // Clearance Handbook")
    st.info(L["t6_info"])
    
    # Render manuals based on the selected language
    if sys_lang == "简体中文":
        with st.expander(L["t6_exp1"], expanded=True):
            st.markdown("""
            #### 1. 投流素材与真机实拍
            在尼日利亚做清仓批发（B2B2C），素材的**“草根真实性”**远比精致画风重要：
            - 安排本地拉各斯的黑人仓库管理员，直接手持商品进行“重力、水淋、硬度”测试。
            - 严禁使用单纯的国内电商白底图进行Meta广告投放，这会让买家认为这是一家“皮包网站”或“预售诈骗”。
            - Meta 广告中主打 `WhatsApp Message` 跳转，把客户全部导入私域沉淀。
            
            #### 2. 定向地区漏斗
            - 尼日利亚主要消费力在 **Lagos（拉各斯）** 及其周边。起步测试只投放拉各斯市（Lagos State）。
            - 预算量大时，再拓宽至 Abuja（阿布贾）、Port Harcourt（哈科特港）。不要投放极度偏远及有安全隐患的北方各州（如 Borno 等）。
            """)
            
        with st.expander(L["t6_exp2"], expanded=False):
            st.markdown("""
            #### 1. 建立 WhatsApp 专属清仓群 (Clearance Broadcast Groups)
            - 客服号一旦有买家咨询，在解答完基础问题后，无论成交与否，必须发送进群链接：
              > *"Chief, join our VIP Container Importers Group to get 20% discount on next arrivals! Free to join!"*
            - 在 WhatsApp 中建立**广播列表 (Broadcast Lists)**，方便进行大批量通知，且不容易因 group 频繁发言被封号。
            
            #### 2. 每日清仓特卖闪购 (Daily Flash Sale)
            - 每天拉各斯时间下午 3 点（国内晚上 10 点），在群内发布“今日特惠”（白底水印图 + 清仓价 + MOQ 限制），刺激代理拿货。
            """)
            
        with st.expander(L["t6_exp3"], expanded=False):
            st.markdown("""
            #### 1. 自提仓（Warehouse Pickup）核心防骗 SOP
            - **严防“假截图”诈骗**：本地客户付款时非常流行发送虚假的银行转账单（Fake Transfer Receipt / SMS alerts）。
            - **货权交接准则**：
              1. 客户到仓，必须先由中方财务在手机银行（如 Sterling Bank, Zenith, GTBank 真实 App 余额）核实**钱已入账且可提现**。
              2. 坚决不能仅凭客户提供的纸质/电子回单直接放货。
              3. 仓管经理必须见财务手签的“放行单 (Gate Pass)”方可将货物装车。
            
            #### 2. 货到付款 (COD) 配送风控
            - 如果客户申请派送货到付款：
              - 仅限拉各斯核心城区，且必须由平台长期合作的、信用良好的本地摩托车骑手（Riders / Logistics Agents）派送。
              - 严禁使用客户临时指定的路边骑手，防范骑手卷款跑路。
              - 对于大宗高价值货物（如几十条轮胎），必须要求客户先支付**双程运费作为诚意金**，否则不予排单。
            """)
            
        with st.expander(L["t6_exp4"], expanded=False):
            st.markdown("""
            | 序号 | 客户常规问题 (Nigerian Client) | 客服推荐处理逻辑 (SOP Logic) | 核心话术参考 (Script Hint) |
            | :--- | :--- | :--- | :--- |
            | **1** | *"Can I buy 1 piece?"* (我只买1个) | 坚决阻断，维护批发门槛。引导他们凑单。 | 使用 Tab 3 的 **起批量说明话术** 快速应答。 |
            | **2** | *"Is this real Chinese copy or original?"* (真的还是假货) | 非洲买家追求“Original”（原装正品）。强调集装箱直进，质量坚固。 | *"Na direct import from container, original quality!"* |
            | **3** | *"Send me bank account."* (要账号) | 给出且仅给出 Sidebar 里配置的企业收款账户，并在末尾标注防骗声明。 | 使用 Tab 3 的 **付款对账话术** 快速应答。 |
            | **4** | *"I want to pay on delivery, but I am in Abuja."* (异地货到付款) | 解释异地无法直接 COD。要求先付运费，或者让他们派拉各斯的朋友来仓库现场验货自提。 | *"You can send your Lagos logistics rider to pick up from warehouse!"* |
            """)

    elif sys_lang == "English":
        with st.expander(L["t6_exp1"], expanded=True):
            st.markdown("""
            #### 1. Targeting Creative Materials
            For clearance wholesale (B2B2C) in Nigeria, **raw warehouse realism** beats polished design every time:
            - Have your local Lagos warehouse worker perform stress-tests (jumping, heavy loads, hitting) on camera.
            - Never use generic catalog photos on Facebook; local buyers will flag it as a preorder scam.
            - Focus meta ads on `WhatsApp Message` button, funneling all traffic to private chats.
            
            #### 2. Geographic Funnels
            - Target only **Lagos State** for initial tests. Lagos contains 70% of local clearance purchasing power.
            - Avoid northern states due to high delivery logistics fees and security risks.
            """)
            
        with st.expander(L["t6_exp2"], expanded=False):
            st.markdown("""
            #### 1. Setup WhatsApp Broadcast Channels
            - Once a customer makes an inquiry, invite them to join the vip warehouse group immediately:
              > *"Chief, join our VIP Container Importers Group to get 20% discount on next arrivals! Free to join!"*
            - Use WhatsApp **Broadcast Lists** to bypass spam blocks instead of over-posting in public groups.
            
            #### 2. Daily Flash Clearances
            - Post clearance deals daily at 3:00 PM Lagos Time with raw white-background images and clear pricing.
            """)
            
        with st.expander(L["t6_exp3"], expanded=False):
            st.markdown("""
            #### 1. Warehouse Self-Pickup Anti-Fraud Guide
            - **Beware of Fake Transfers**: Buyers often show forged screenshots or fake bank SMS alerts.
            - **Release SOP**:
              1. Finance must log in to the corporate bank app (Sterling/Zenith/GTB) and confirm **funds are settled in balance**.
              2. Do NOT release goods based on buyer's paper/phone receipt.
              3. The gate supervisor must receive a signed **Gate Pass** before loading.
            
            #### 2. Cash on Delivery (COD) Rules
            - COD is strictly limited to central Lagos State using vetted local riders.
            - For heavy B2B orders, ask for a **commitment transport fee** before dispatching.
            """)
            
        with st.expander(L["t6_exp4"], expanded=False):
            st.markdown("""
            | No. | Customer Inquiry | Recommended Action | Reply Phrase |
            | :--- | :--- | :--- | :--- |
            | **1** | *"Can I buy 1 piece?"* | Politely decline to protect MOQ threshold. | Use Tab 3 **Wholesale MOQ Rules** script. |
            | **2** | *"Is this original?"* | Reassure they are imported direct containers. | *"Na direct import from container, original quality!"* |
            | **3** | *"Send bank details"* | Send only corporate account details and display anti-fraud warning. | Use Tab 3 **Official Account** script. |
            | **4** | *"Send it to Abuja COD"* | Decline COD for far cities. Ask for pickup in Lagos. | *"Send your Lagos logistics rider to pick up from warehouse!"* |
            """)

    else: # Nigerian Pidgin Manual
        with st.expander(L["t6_exp1"], expanded=True):
            st.markdown("""
            #### 1. Correct Ads material
            If you wan run ads for Naija, no use fine packaging logo. Local buyers wan see **wetin dey happen inside warehouse**:
            - Make local Lagos boy jump on chair or roll tyre on ground for camera. Local buyers like *Durable* thing.
            - Don't use fine graphics. Raw video from warehouse gets more trust.
            - Set Facebook ads to click straight to WhatsApp.
            
            #### 2. Location to Target
            - Put your ads only for **Lagos State** first. No waste money target north side, delivery cost go kill your profit.
            """)
            
        with st.expander(L["t6_exp2"], expanded=False):
            st.markdown("""
            #### 1. Build VIP WhatsApp Group
            - As customer message you finish, tell them to join broadcast group sharp-sharp:
              > *"Chief, join our VIP Container Importers Group to get 20% discount on next arrivals! Free to join!"*
            - Keep customer contact safe inside WhatsApp list make you dey message them every week.
            """)
            
        with st.expander(L["t6_exp3"], expanded=False):
            st.markdown("""
            #### 1. How to avoid Fake Alerts inside Lagos Warehouse
            - **No trust SMS alert or screenshot**: Buyers fit design fake bank alert send you.
            - **Rules for Release**:
              1. Finance manager must open bank app, check account balance, verify say money don enter inside the account.
              2. No allow driver carry cargo out of warehouse gate if finance never sign **Gate Pass**.
            
            #### 2. Cash on Delivery (COD) Delivery
            - Only send COD inside Lagos center using trusted riders. No send big bulk cargo without upfront transport fee!
            """)
            
        with st.expander(L["t6_exp4"], expanded=False):
            st.markdown("""
            | No. | Customer Chat | Wetin you go do | Reply Script |
            | :--- | :--- | :--- | :--- |
            | **1** | *"Can I buy 1 piece?"* | Tell them MOQ is strict wholesale price. | Use Tab 3 **Why MOQ high** script. |
            | **2** | *"Is this original?"* | Tell them na direct container landing. | *"Aje o! Na direct container, original quality!"* |
            | **3** | *"Send bank details"* | Give official corporate bank account only. | Use Tab 3 **Official Account Details** script. |
            | **4** | *"Send it to Abuja COD"* | Tell them Abuja is far, only Lagos is COD. | *"Send your Lagos logistics rider to pick up from warehouse!"* |
            """)
