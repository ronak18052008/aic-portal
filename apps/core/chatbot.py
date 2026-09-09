from apps.taxonomy.models import Field
from apps.education.models import Course, Programme, Certification
from apps.institutions.models import Institution
from apps.opportunities.models import Opportunity
from apps.skills.models import Skill

def get_role_quick_prompts(role: str) -> list:
    """Returns tailored prompt starters based on the user's role."""
    prompts_by_role = {
        'STUDENT': [
            "How do I bridge my skill gap for an AI Engineer role?",
            "Which industry certifications are recommended for Cloud & DevOps?",
            "How do I generate and verify my AIC Passport?",
            "What paid internships are currently available in Bengaluru or remote?",
            "How can I use the AI Resume Builder to tailor my CV?"
        ],
        'ACADEMICIAN': [
            "How do I align curriculum design with NEP 2020 frameworks?",
            "Where can I find research collaboration opportunities with industry?",
            "How do I evaluate student competencies using AIC Passport evidence?",
            "What Faculty Development Programmes (FDP) are available?"
        ],
        'INDUSTRY': [
            "How do I post a verified job or internship opportunity?",
            "How can I discover pre-screened talent by verified skill match score?",
            "What are the top NIRF-ranked institutions for semiconductor engineering?",
            "How do I verify candidate AIC Passports cryptographically?"
        ],
        'INSTITUTION': [
            "What are the key NAAC Grade and NIRF ranking criteria on the portal?",
            "How do we track student placement and employment outcomes?",
            "How can we list our UGC-recognized online degree programmes?",
            "How do we set up industry mentorship partnerships for our campus?"
        ],
        'SYSTEM_ADMIN': [
            "What is the current verification and source provenance status?",
            "How do I configure new taxonomy disciplines and subfields?",
            "Show me a summary of total users, institutions, and live offerings."
        ]
    }
    return prompts_by_role.get(role, [
        "What is the AIC Portal and how does it connect academia with industry?",
        "How do I search for verified degree programmes and global courses?",
        "How do I create a student, faculty, or recruiter account?"
    ])

def process_ai_chat(message: str, user, role: str) -> str:
    """
    Intelligent role-aware AI chatbot assistant grounded in the AIC ecosystem database.
    """
    msg = message.lower().strip()
    user_name = user.get_full_name() if (user and user.is_authenticated) else "Scholar"

    # 1. AIC Passport & QR Code queries
    if "passport" in msg or "qr" in msg or "credential" in msg or "verify" in msg:
        return (
            f"Hello {user_name}! The **AIC Passport** is your sovereign, cryptographically verified record "
            f"of academic and technical competencies on the AIC Portal.\n\n"
            f"• **Auto-Generated QR Code**: Every passport features a real, scannable QR code linking to your secure public verification endpoint.\n"
            f"• **Verified Evidence**: Credentials earned from assessments, accredited coursework, and verified project submissions are permanently stamped.\n"
            f"• **Sharing**: Employers and recruiters can scan your QR code directly or visit your unique verification token URL to confirm authentic credentials.\n\n"
            f"You can view, print, or download your official QR code anytime at [/passport/](/passport/)."
        )

    # 2. Resume Builder queries
    if "resume" in msg or "cv" in msg or "builder" in msg:
        return (
            f"Hi {user_name}! Our **AI Resume & CV Studio** makes it easy to generate recruiter-ready resumes in minutes:\n\n"
            f"1. **Photo Integration**: Displays your official profile photo or a custom upload.\n"
            f"2. **4 Unique Templates**: Switch instantly between *Modern Tech*, *Executive Minimalist*, *Creative Aurora*, and *Academic CV*.\n"
            f"3. **AI Enhancement**: Click 'AI Enhance Summary' or generate bullet points tailored to your target job title.\n"
            f"4. **PDF Download**: Export high-resolution, print-ready PDF files instantly with your AIC Passport QR badge included.\n\n"
            f"Try it now at [/resume/builder/](/resume/builder/)!"
        )

    # 3. Skill Gap & Career Roadmap
    if "skill gap" in msg or "bridge" in msg or "roadmap" in msg:
        return (
            f"Great question! The **Skill Gap Analysis Engine** compares your verified competencies against industry job requirements.\n\n"
            f"• Select your target career role (e.g. *AI Backend Engineer*, *Data Scientist*, *Cloud Architect*).\n"
            f"• The engine calculates your matched competencies and flags critical missing skills.\n"
            f"• It automatically suggests targeted courses and learning tracks to bridge your gap.\n\n"
            f"Check your real-time gap analysis at [/skills/gap/](/skills/gap/) or view your career roadmap at [/career/roadmap/](/career/roadmap/)."
        )

    # 4. Certifications
    if "certification" in msg or "certificate" in msg:
        top_certs = Certification.objects.all()[:3]
        certs_list = "\n".join([f"• **{c.title}** by *{c.issuing_organization}* ({c.get_level_display()})" for c in top_certs])
        return (
            f"The AIC Portal hosts 25+ verified global industry certifications from premier organizations (AWS, Google Cloud, Microsoft, Linux Foundation, etc.).\n\n"
            f"**Featured Certifications:**\n{certs_list}\n\n"
            f"Browse all certifications with smart discipline and organization filters at [/certifications/](/certifications/)."
        )

    # 5. Internships & Jobs / Opportunities
    if "internship" in msg or "job" in msg or "hiring" in msg or "career" in msg or "apply" in msg:
        if role == 'INDUSTRY':
            return (
                f"As an Industry partner, you can post verified employment opportunities and search candidates by skill match:\n\n"
                f"• **Post a Job/Internship**: Go to [/opportunities/create/](/opportunities/create/) to publish roles with required skills and compensation.\n"
                f"• **Applicant Tracking**: Review candidate submissions and AIC Passports at [/applications/manage/](/applications/manage/).\n"
                f"• **Candidate Matching**: Filter candidates by skill percentage and verified assessment credentials."
            )
        else:
            top_opps = Opportunity.objects.all()[:3]
            opps_list = "\n".join([f"• **{o.title}** at *{o.organization_name}* ({o.city}, {o.country})" for o in top_opps])
            return (
                f"There are currently 80+ live, verified opportunities from leading organizations:\n\n"
                f"{opps_list}\n\n"
                f"You can discover and apply for roles with one click at [/search/?type=jobs](/search/?type=jobs) or [/search/?type=internships](/search/?type=internships)."
            )

    # 6. Academician / NEP 2020 / Research
    if role == 'ACADEMICIAN' or "nep" in msg or "curriculum" in msg or "research" in msg or "grant" in msg:
        return (
            f"Greetings, Professor {user_name}! The AIC Platform empowers academicians with tools aligned to NEP 2020 guidelines:\n\n"
            f"• **Curriculum Alignment**: Map departmental courses to industry skills using our taxonomy of 20 fields and 81 subfields.\n"
            f"• **Research Grants & Projects**: Explore industry-sponsored research opportunities at [/research/](/research/).\n"
            f"• **Student Mentorship**: Guide students through capstone projects and internship pipelines at [/mentorship/](/mentorship/).\n"
            f"• **Faculty Development**: Discover FDP and upskilling courses across emerging disciplines."
        )

    # 7. Institution / NAAC / NIRF
    if role == 'INSTITUTION' or "nirf" in msg or "naac" in msg or "placement" in msg:
        return (
            f"Welcome, Institution Leader! Here is how AIC supports institutional excellence:\n\n"
            f"• **NIRF & NAAC Benchmarking**: Directory of 104+ accredited universities with rankings and NAAC grades at [/institutions/](/institutions/).\n"
            f"• **Department Analytics**: Inspect departmental skill heatmaps at [/institutions/heatmap/](/institutions/heatmap/).\n"
            f"• **Placement Tracking**: Monitor real-time graduate employment and corporate joining records at [/institutions/placement/](/institutions/placement/).\n"
            f"• **Degree Listing**: Publish UGC-recognized offline, online, and hybrid degree programmes to our global discovery ecosystem."
        )

    # 8. Settings & Preferences
    if "setting" in msg or "profile" in msg or "password" in msg or "notification" in msg:
        return (
            f"You can manage your account, security, and role-specific preferences at [/settings/](/settings/):\n\n"
            f"• **Account Details**: Update name, headline, contact info, and profile photo.\n"
            f"• **Role Preferences**: Customize career discovery visibility, mentorship availability, or recruiter alerts.\n"
            f"• **Notifications**: Toggle email digests and alert frequencies.\n"
            f"• **Security**: Change your password and audit active sessions."
        )

    # 9. General Default Guidance
    total_inst = Institution.objects.count()
    total_courses = Course.objects.count()
    total_opps = Opportunity.objects.count()
    return (
        f"Hello {user_name}! I am your **AIC Ecosystem AI Assistant**, specialized for your role as **{role.capitalize()}**.\n\n"
        f"I can help you explore:\n"
        f"• **{total_inst} Verified Universities & Institutions** ([/institutions/](/institutions/))\n"
        f"• **{total_courses} Global Degree & Online Courses** ([/search/?type=courses](/search/?type=courses))\n"
        f"• **{total_opps} Live Jobs & Internships** ([/search/?type=jobs](/search/?type=jobs))\n"
        f"• **AI Resume & CV Studio** ([/resume/builder/](/resume/builder/))\n"
        f"• **AIC Passport & QR Verification** ([/passport/](/passport/))\n"
        f"• **Skill Gap Analysis & Roadmaps** ([/skills/gap/](/skills/gap/))\n\n"
        f"Feel free to ask any specific question about degrees, skills, careers, research, or portal features!"
    )
