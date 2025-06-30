# i18n.py
LANGUAGES = {
    "en": {
        "language": "🌍 Language",
        "title": "RESUMIX · Smart Resume Assistant",
        "upload_resume": "📎 Upload Resume",
        "upload_resume_title": "Upload your resume PDF file",
        "job_description": "💼 Job Description",
        "job_description_title": "Job Description URL",
        "user_login": "👤 User Login",
        "login_button": "Login",
        "login_success": "Login Success",
        "invalid_credentials": "Invalid credentials",
        "logged_in": "Logged in",
        "logout": "Logout",
        "please_upload": "Please upload a resume PDF file to get started.",
        "tabs": ["Parsing", "Polish", "Agent", "Score", "Compare"],
        
        # Analysis Card
        "analysis": {
            "please_upload": "📄 Please upload a resume to begin analysis",
            "sections_detected": "Detected Resume Sections:",
            "section_content": "Section content:",
        },
        
        # Polish Card
        "polish": {
            "please_upload": "✨ Please upload a resume to begin polishing",
            "using_cached": "💾 **Using cached results** - Switch to a different tab and back to refresh with new AI suggestions",
            "results_cached": "💾 **Results cached!** Your polishing suggestions will be preserved when you return to this tab.",
            "regenerate_button": "🔄 Regenerate AI Suggestions",
            "regenerate_help": "Clear cache and get fresh AI polishing suggestions",
            "polishing_sections": "✨ **Polishing {count} sections:** {sections}",
            "ai_polishing": "AI is polishing {section}...",
        },
        
        # Compare Card
        "compare": {
            "original": "Original",
            "polished": "Polished",
            "title": "✨ Resume Polish",
            "description": "Please recommend improvements for the following resume section:\n\n{content}",
            "result": "Polished Result",
            "please_upload": "🔄 Please upload and analyze a resume first",
            "ready_to_compare": "💾 **Ready to compare!** Found polish results for {count} sections",
            "no_polish_results": "⚠️ **No polish results found**",
            "visit_polish_first": "💡 Please visit the Polish tab first to generate AI suggestions, then return here to compare",
            "no_polish_available": "⚠️ No polished content available. Please use the Polish tab first to generate AI suggestions.",
            "switch_to_polish": "💡 Switch to the Polish tab to get AI-powered improvements for this section.",
            "original_content": "Here is the content from the resume:",
            "polished_content": "Here is the polished content:",
            "using_cached_results": "💾 Using cached polish results ({count} sections)",
            "no_results_found": "⚠️ No polish results found. Please visit the Polish tab first to generate AI suggestions.",
            "polish_tab_info": "💡 The Polish tab will generate AI-powered improvements that can then be compared here.",
            "comparing_sections": "🔄 **Comparing {count} sections:** {sections}",
        },
    },
    "zh": {
        "language": "🌍 语言",
        "title": "RESUMIX · 智能简历助手",
        "upload_resume": "📎 上传简历",
        "upload_resume_title": "上传您的简历 PDF 文件",
        "job_description": "💼 岗位描述",
        "job_description_title": "岗位描述链接",
        "user_login": "👤 用户登录",
        "login_button": "登录",
        "login_success": "登录成功",
        "invalid_credentials": "账号或密码错误",
        "logged_in": "已登录",
        "logout": "退出登录",
        "please_upload": "请上传 PDF 格式简历开始使用。",
        "tabs": ["简历解析", "推荐优化", "智能代理", "简历评分", "简历对比"],
        
        # Analysis Card
        "analysis": {
            "please_upload": "📄 请上传简历开始分析",
            "sections_detected": "检测到的简历章节：",
            "section_content": "章节内容：",
        },
        
        # Polish Card
        "polish": {
            "please_upload": "✨ 请上传简历开始润色",
            "using_cached": "💾 **使用缓存结果** - 切换到其他标签页再回来可刷新获取新的AI建议",
            "results_cached": "💾 **结果已缓存！** 当您返回此标签页时，润色建议将被保留。",
            "regenerate_button": "🔄 重新生成AI建议",
            "regenerate_help": "清除缓存并获取新的AI润色建议",
            "polishing_sections": "✨ **正在润色 {count} 个章节：** {sections}",
            "ai_polishing": "AI正在润色 {section}...",
        },
        
        # Compare Card
        "compare": {
            "original": "原文",
            "polished": "优化后",
            "title": "✨ 简历优化",
            "description": "请推荐以下简历段落的改进建议：\n\n{content}",
            "result": "优化结果",
            "please_upload": "🔄 请先上传并分析简历",
            "ready_to_compare": "💾 **准备好对比！** 找到 {count} 个章节的润色结果",
            "no_polish_results": "⚠️ **未找到润色结果**",
            "visit_polish_first": "💡 请先访问润色标签页生成AI建议，然后返回这里进行对比",
            "no_polish_available": "⚠️ 无可用的润色内容。请先使用润色标签页生成AI建议。",
            "switch_to_polish": "💡 切换到润色标签页获取AI驱动的改进建议。",
            "original_content": "以下是简历中的内容：",
            "polished_content": "这是润色后的内容：",
            "using_cached_results": "💾 使用缓存的润色结果（{count} 个章节）",
            "no_results_found": "⚠️ 未找到润色结果。请先访问润色标签页生成AI建议。",
            "polish_tab_info": "💡 润色标签页将生成AI驱动的改进建议，然后可以在这里进行对比。",
            "comparing_sections": "🔄 **对比 {count} 个章节：** {sections}",
        },
    },
}
