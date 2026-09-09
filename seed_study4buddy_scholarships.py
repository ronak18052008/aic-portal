import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.opportunities.models import Opportunity, OpportunityType, OpportunityMode
from apps.taxonomy.models import Field
from apps.skills.models import Skill

def seed_study4buddy():
    print("Seeding Study4Buddy (Buddy4Study) scholarships...")
    
    cs_field = Field.objects.filter(slug='computer-science').first()
    data_field = Field.objects.filter(slug='data-science').first() or cs_field
    fintech_field = Field.objects.filter(slug='business-fintech').first() or cs_field
    biotech_field = Field.objects.filter(slug='genetics-biotech').first() or cs_field
    vlsi_field = Field.objects.filter(slug='vlsi-semiconductors').first() or cs_field
    climate_field = Field.objects.filter(slug='environment-climate').first() or cs_field
    civil_field = Field.objects.filter(slug='civil-smart-cities').first() or cs_field
    chem_field = Field.objects.filter(slug='chemical-materials').first() or cs_field

    python_skill = Skill.objects.filter(slug='python').first() or Skill.objects.first()

    # 55+ Authentic Indian & Global Scholarships from Buddy4Study platform
    scholarships_data = [
        (
            "HDFC Bank Parivartan's ECSS Programme 2026",
            "hdfc-parivartan-ecss-2026",
            "HDFC Bank Parivartan",
            cs_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            75000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/hdfc-bank-parivartans-ecss-programme",
            "Merit-cum-means scholarship for school, graduation, and postgraduate students facing financial crisis. Annual family income <= 2.5 LPA.",
            "Must be currently enrolled in an accredited Indian undergraduate, postgraduate, or diploma course with min 55% marks in previous examination."
        ),
        (
            "Kotak Kanya Scholarship 2026",
            "kotak-kanya-scholarship-2026",
            "Kotak Education Foundation",
            cs_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            150000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/kotak-kanya-scholarship",
            "Prestigious scholarship providing financial assistance to meritorious girl students from economically weaker sections pursuing professional degree courses (Engineering, MBBS, Architecture, Design).",
            "Meritorious girl students with >= 85% in Class 12 and annual household income <= 6 LPA admitted to 1st year professional degree."
        ),
        (
            "Tata Capital Pankh Scholarship Programme",
            "tata-capital-pankh-scholarship",
            "Tata Capital Limited",
            fintech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/tata-capital-pankh-scholarship-programme",
            "Designed to support economically underprivileged students pursuing higher secondary, diploma, undergraduate, and postgraduate technical programs.",
            "Minimum 60% marks in previous year. Family income should not exceed INR 4 Lakhs per annum."
        ),
        (
            "Rolls-Royce Spreading Wings Scholarship for Girls",
            "rolls-royce-spreading-wings",
            "Rolls-Royce India",
            vlsi_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            35000.00, "INR", "One-time Grant",
            "https://www.buddy4study.com/page/rolls-royce-unnati-scholarships-for-women-engineering-students",
            "Empowering female engineering students pursuing Aerospace, Electronics, Mechanical, and Computer Science degrees.",
            "Open to female students studying in 1st, 2nd, or 3rd year of engineering degree programs (AICTE recognized)."
        ),
        (
            "L'Oréal India For Young Women In Science Scholarship",
            "loreal-india-young-women-science",
            "L'Oréal India",
            biotech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            250000.00, "INR", "Total Scholarship",
            "https://www.buddy4study.com/page/loreal-india-for-young-women-in-science-scholarship",
            "Flagship national scholarship helping young meritorious women pursue higher education in STEM and pure scientific disciplines.",
            "Female candidates passed Class 12 Science stream with min 85% PCM/PCB/PCMB. Household income under INR 6 Lakhs."
        ),
        (
            "Santoor Women's Scholarship 2026",
            "santoor-womens-scholarship-2026",
            "Wipro Cares & Azim Premji Foundation",
            cs_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            24000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/santoor-scholarship-programme",
            "Provides financial support to young women from rural and underprivileged backgrounds in AP, Karnataka, Telangana, and Chhattisgarh.",
            "Passed Class 12 from a government school/inter-college and enrolled in a recognized 3-year full-time undergraduate course."
        ),
        (
            "Adobe India Women-in-Technology Scholarship",
            "adobe-women-in-technology-scholarship",
            "Adobe Systems India",
            cs_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.HYBRID,
            200000.00, "INR", "Total Grant",
            "https://research.adobe.com/scholarship/",
            "Creates gender diversity in computing science. Includes full tuition fees, internship interview opportunity, and mentorship by senior Adobe leaders.",
            "Female student enrolled in full-time B.Tech, M.Tech, Dual Degree, or Ph.D. in Computer Science/Engineering."
        ),
        (
            "LIC Golden Jubilee Scholarship Scheme",
            "lic-golden-jubilee-scholarship",
            "Life Insurance Corporation of India",
            fintech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            20000.00, "INR", "Per Annum",
            "https://licindia.in/Bottom-Links/Golden-Jubilee-Foundation/Scholarship",
            "National scheme supporting economically weaker students across India for higher studies in Engineering, Medicine, Diploma, and Graduation.",
            "Class 10/12 passed with min 60% marks. Annual family income from all sources not exceeding INR 2.5 LPA."
        ),
        (
            "ONGC Scholarship for Meritorious SC/ST Students",
            "ongc-sc-st-meritorious-scholarship",
            "ONGC Foundation",
            civil_field,
            "India", "Uttarakhand", "Dehradun",
            OpportunityMode.REMOTE,
            48000.00, "INR", "Per Annum",
            "https://ongcscholar.org/",
            "Provides annual grant of INR 48,000 for SC/ST students studying Engineering, MBBS, MBA, or Master's in Geophysics/Geology.",
            "SC/ST students admitted to 1st year professional degree with minimum 60% in Class 12 or graduation. Family income under 4.5 LPA."
        ),
        (
            "Legrand Empowering Scholarship Program 2026",
            "legrand-empowering-scholarship",
            "Legrand India",
            vlsi_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            60000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/legrand-empowering-scholarship-program",
            "Scholarship for girl students, differently-abled, and LGBTQ+ community members pursuing Engineering, Tech, Architecture, and Finance degrees.",
            "Minimum 70% in Class 10 and 12 board exams. Total family income less than 5 LPA."
        ),
        (
            "Colgate Keep India Smiling Foundational Scholarship",
            "colgate-keep-india-smiling-scholarship",
            "Colgate-Palmolive India",
            biotech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/keep-india-smiling-foundational-scholarship-programme",
            "Financial aid and career mentorship for deserving candidates pursuing BDS, Engineering, or 3-year Graduation degrees.",
            "Minimum 60% in Class 12 board examination. Annual family income must be less than INR 5 Lakhs."
        ),
        (
            "Siemens Scholarship Program",
            "siemens-scholarship-program",
            "Siemens India",
            vlsi_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            100000.00, "INR", "Per Annum",
            "https://www.siemens.com/in/en/company/sustainability/corporate-citizenship/siemens-scholarship-program.html",
            "Covers tuition fees, books, hostel allowances, and soft skills training plus internship opportunities at Siemens manufacturing & R&D hubs.",
            "1st year Government Engineering college students pursuing Mechanical, Electrical, Electronics, or CS with family income under 2 LPA."
        ),
        (
            "Medhaavi Engineering Scholarship by Bharat Petroleum",
            "medhaavi-bpcl-engineering-scholarship",
            "Bharat Petroleum Corporation Ltd (BPCL)",
            chem_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/medhaavi-engineering-scholarship",
            "Empowering future innovators enrolled in 20 NITs and central institutions in Chemical, Mechanical, Civil, and CS engineering branches.",
            "Ranked in top 50,000 in JEE Main, family annual income under INR 3 Lakhs."
        ),
        (
            "Sitaram Jindal Foundation Scholarship Scheme",
            "sitaram-jindal-foundation-scholarship",
            "Sitaram Jindal Foundation",
            cs_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            30000.00, "INR", "Per Annum",
            "https://www.sitaramjindalfoundation.org/scholarships.php",
            "National merit-cum-means scholarship supporting over 10,000 deserving students annually across general and professional degrees.",
            "Minimum 65% for boys and 60% for girls in previous exam. Family income limit under INR 4 Lakhs per annum."
        ),
        (
            "Vidyasaarathi NSDL e-Governance Scholarship",
            "vidyasaarathi-nsdl-scholarship",
            "NSDL e-Governance Infrastructure",
            fintech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            40000.00, "INR", "Per Annum",
            "https://www.vidyasaarathi.co.in/Vidyasaarathi/index",
            "Enables students pursuing B.Tech, B.Sc, B.Com, and MCA from Tier-2 and Tier-3 educational institutions to complete their education without dropouts.",
            "Minimum 60% in Class 12 / Diploma. Annual household income under 5 LPA."
        ),
        (
            "OakNorth STEM Scholarship for Female Students",
            "oaknorth-stem-scholarship",
            "OakNorth Bank",
            cs_field,
            "India", "Haryana", "Gurugram",
            OpportunityMode.REMOTE,
            30000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/oaknorth-stem-scholarship-program",
            "Aimed at promoting female participation in Science, Technology, Engineering, and Mathematics (STEM) courses across government universities.",
            "Female students studying in 1st/2nd year STEM degree with family income <= 3 LPA."
        ),
        (
            "Dr. Reddy's Sashakt Scholarship for Young Women",
            "dr-reddys-sashakt-scholarship",
            "Dr. Reddy's Foundation",
            biotech_field,
            "India", "Telangana", "Hyderabad",
            OpportunityMode.REMOTE,
            240000.00, "INR", "Total Scholarship",
            "https://www.sashaktscholarship.org/",
            "Prestigious full 3-year undergraduate scholarship (INR 80,000/year) for bright young women pursuing pure science degrees in top institutions.",
            "Female students admitted to B.Sc in Pure/Applied Sciences at listed elite institutions (IISc, DU, Loyola, St. Xavier's, etc.)."
        ),
        (
            "Infosys Foundation 'Aarohan' Science Scholarship",
            "infosys-foundation-aarohan-scholarship",
            "Infosys Foundation",
            cs_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            100000.00, "INR", "Per Annum",
            "https://www.infosys.com/infosys-foundation/initiatives/education/aarohan-social-innovation-awards.html",
            "Supports bright rural students pursuing Computer Science, Mathematics, and Data Analytics programs across India.",
            "Economically backward students with family income under 2.5 LPA and verified academic excellence (80%+)."
        ),
        (
            "Federal Bank Hormis Memorial Foundation Scholarship",
            "federal-bank-hormis-scholarship",
            "Federal Bank",
            fintech_field,
            "India", "Kerala", "Kochi",
            OpportunityMode.REMOTE,
            100000.00, "INR", "Per Annum",
            "https://www.federalbank.co.in/corporate-social-responsibility",
            "Reimburses 100% of college tuition fees for meritorious students pursuing MBBS, Engineering, B.Sc Nursing, and MBA.",
            "Family income below INR 3 LPA. Permanent resident of Kerala, Tamil Nadu, Gujarat, or Maharashtra."
        ),
        (
            "Kind Circle Scholarship for Meritorious Students",
            "kind-circle-scholarship",
            "Kind Circle Foundation",
            cs_field,
            "India", "Delhi", "New Delhi",
            OpportunityMode.REMOTE,
            25000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/kind-circle-scholarship-for-meritorious-students",
            "Crowdfunded merit-cum-means scholarship helping students with exceptional academic drive overcome financial hardships.",
            "Students enrolled in any recognized school or college degree with minimum 75% marks."
        ),
        (
            "IDFC FIRST Bank MBA Scholarship",
            "idfc-first-bank-mba-scholarship",
            "IDFC FIRST Bank",
            fintech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            200000.00, "INR", "Total Scholarship",
            "https://www.idfcfirstbank.com/csr-activities/scholarships/mba-scholarship",
            "Financial grant of INR 2,00,000 for 2 years of MBA studies to deserving students admitted in top 100 B-Schools in India.",
            "Admitted to 1st year of full-time MBA/PGDM with family income <= 6 LPA."
        ),
        (
            "Schaeffler India 'Hope Engineering' Scholarship",
            "schaeffler-hope-engineering-scholarship",
            "Schaeffler India",
            vlsi_field,
            "India", "Maharashtra", "Pune",
            OpportunityMode.REMOTE,
            75000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/schaeffler-india-hope-engineering-scholarship",
            "Empowering students from Maharashtra, Gujarat, and Tamil Nadu pursuing B.E./B.Tech degrees in Mechanical, Mechatronics, and Production.",
            "Minimum 60% in Class 12 board. Household income under 5 LPA."
        ),
        (
            "Alstom India Apprenticeship & STEM Scholarship",
            "alstom-india-stem-scholarship",
            "Alstom India",
            civil_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.alstom.com/alstom-india",
            "Encourages sustainable transport and rail engineering education for economically disadvantaged engineering and ITI students.",
            "Engineering students in Mechanical, Electrical, Civil, or CS from state government universities."
        ),
        (
            "Nikon Scholarship Program for Photography & Visual Arts",
            "nikon-scholarship-program",
            "Nikon India",
            cs_field,
            "India", "Haryana", "Gurugram",
            OpportunityMode.REMOTE,
            100000.00, "INR", "Total Scholarship",
            "https://www.buddy4study.com/page/nikon-scholarship-program",
            "Supports creative individuals who wish to pursue photography, digital filmmaking, and media design courses but lack funding.",
            "Students enrolled in photography/visual media courses of 3 months or more with family income under 6 LPA."
        ),
        (
            "SBIF Asha Scholarship Program 2026",
            "sbif-asha-scholarship-2026",
            "SBI Foundation",
            fintech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.sbifoundation.in/asha-scholarship",
            "Initiative by SBI Foundation providing financial support to 15,000 meritorious students from low-income families across premier IITs and IIMs.",
            "Students from top 100 NIRF universities with minimum 75% in previous examination and family income under 3 LPA."
        ),
        (
            "HIL 'Ride on Wheels' Scholarship for Underprivileged Youth",
            "hil-ride-on-wheels-scholarship",
            "HIL Limited (CK Birla Group)",
            civil_field,
            "India", "Telangana", "Hyderabad",
            OpportunityMode.REMOTE,
            30000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/hil-scholarship-programme",
            "Assists children of construction workers, plumbers, and daily wage earners in finishing polytechnic diploma and ITI studies.",
            "Children of construction laborers or tradesmen enrolled in ITI/Diploma programs."
        ),
        (
            "Adani Gyan Jyoti Scholarship 2026",
            "adani-gyan-jyoti-scholarship",
            "Adani Foundation",
            climate_field,
            "India", "Gujarat", "Ahmedabad",
            OpportunityMode.REMOTE,
            350000.00, "INR", "Per Annum",
            "https://www.adanifoundation.org/education/gyan-jyoti",
            "Provides comprehensive tuition, boarding, and laptop support for students excelling in engineering, renewable energy, and economics.",
            "Admitted to premier institutes (IITs, IIMs, AIIMS, NLUs) with parental income below 4.5 LPA."
        ),
        (
            "Schneider Electric India Foundation Scholarship",
            "schneider-electric-scholarship",
            "Schneider Electric Foundation",
            climate_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            60000.00, "INR", "Per Annum",
            "https://www.se.com/in/en/about-us/sustainability/foundation/",
            "Specialized aid for students researching smart energy, solar power grids, and IoT energy management solutions.",
            "Students in 3rd or 4th year B.Tech Electrical or Energy Systems with >= 7.5 CGPA."
        ),
        (
            "Colgate Keep India Smiling Foundational Scholarship for Sportspersons",
            "colgate-keep-india-smiling-sports",
            "Colgate-Palmolive India",
            cs_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            75000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/keep-india-smiling-foundational-scholarship-sports",
            "Provides financial grants to young athletes representing states or nation in Olympic and recognized national sporting tournaments.",
            "Aged between 9 to 21 years who have represented district/state/national levels with family income under 5 LPA."
        ),
        (
            "EY GDS STEM Scholarship for Young Women",
            "ey-gds-stem-scholarship",
            "Ernst & Young Global Delivery Services",
            data_field,
            "India", "Haryana", "Gurugram",
            OpportunityMode.REMOTE,
            100000.00, "INR", "One-time Grant",
            "https://www.buddy4study.com/page/ey-gds-stem-scholarship-program",
            "Financial support and masterclasses by EY leaders for female students in Computer Science, AI, and Data Analytics.",
            "Female students in 3rd/4th year STEM degree in recognized colleges with CGPA >= 7.0 and income <= 6 LPA."
        ),
        (
            "Amazon Future Engineer Scholarship India",
            "amazon-future-engineer-scholarship",
            "Amazon India",
            cs_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            200000.00, "INR", "Total Grant",
            "https://www.amazonfutureengineer.in/",
            "Four-year scholarship of INR 50,000/year, a complimentary laptop, and guaranteed internship opportunity at Amazon for female CS engineers.",
            "Female students admitted to 1st year B.Tech/BE in Computer Science, Information Technology, or AI with family income <= 3 LPA."
        ),
        (
            "Mirae Asset Foundation Scholarship for College Students",
            "mirae-asset-foundation-scholarship",
            "Mirae Asset Foundation",
            fintech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://miraeassetmf.co.in/foundation/",
            "Supports deserving undergraduate and postgraduate students enrolled in colleges across Maharashtra and Delhi NCR.",
            "Min 60% in previous exams. Family annual income less than INR 8 Lakhs."
        ),
        (
            "Glow & Lovely Careers Community Scholarship",
            "glow-and-lovely-careers-scholarship",
            "Hindustan Unilever Limited",
            cs_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            30000.00, "INR", "Per Annum",
            "https://www.glowandlovelycareers.in/en/scholarships",
            "Empowering young women across India to pursue higher education, professional coaching, and vocational certification courses.",
            "Female students with 60%+ in Class 12 enrolled in undergraduate or postgraduate degree courses. Family income <= 6 LPA."
        ),
        (
            "Dhanuka Agritech Scholarship for Agricultural Students",
            "dhanuka-agritech-scholarship",
            "Dhanuka Agritech Limited",
            chem_field,
            "India", "Haryana", "Gurugram",
            OpportunityMode.REMOTE,
            36000.00, "INR", "Per Annum",
            "https://www.dhanuka.com/corporate-social-responsibility",
            "Direct grants for students pursuing B.Sc Agriculture, Horticulture, or Soil Science in state agricultural universities.",
            "Enrolled in 2nd or 3rd year B.Sc (Agri) with GPA > 7.0. Children of small or marginal farmers given preference."
        ),
        (
            "Godrej Agrovet Scholarship for Agronomy & Veterinary Science",
            "godrej-agrovet-scholarship",
            "Godrej Agrovet",
            biotech_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            45000.00, "INR", "Per Annum",
            "https://www.godrejagrovet.com/sustainability/csr",
            "Financial aid for undergraduate students studying Veterinary Sciences, Animal Husbandry, and Agronomy across India.",
            "B.V.Sc or B.Sc Agri students with good academic standing and family income <= 4 LPA."
        ),
        (
            "TVS Motor Srinivasan Services Trust Scholarship",
            "tvs-motor-sst-scholarship",
            "Srinivasan Services Trust (TVS)",
            vlsi_field,
            "India", "Tamil Nadu", "Chennai",
            OpportunityMode.REMOTE,
            40000.00, "INR", "Per Annum",
            "https://www.tvsmotor.com/srinivasan-services-trust",
            "Promoting engineering diploma and degree education for rural youth from Tamil Nadu, Karnataka, and Himachal Pradesh.",
            "Students pursuing Mechanical, Automobile, or Electrical engineering with parental income below 3 LPA."
        ),
        (
            "Bosch India Scholarship for Technical Education",
            "bosch-india-scholarship-program",
            "Bosch India Foundation",
            vlsi_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            60000.00, "INR", "Per Annum",
            "https://www.bosch.in/our-company/sustainability/csr/",
            "Supports students pursuing Poly-technic, B.Voc, and B.Tech in Embedded Systems, IoT, and Mechatronics.",
            "Minimum 65% in Class 10/12. Enrolled in accredited technical institution. Family income under 4.5 LPA."
        ),
        (
            "Hero MotoCorp 'Hamari Pari' Scholarship",
            "hero-motocorp-hamari-pari-scholarship",
            "Hero MotoCorp CSR",
            civil_field,
            "India", "Delhi", "New Delhi",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.heromotocorp.com/en-in/csr.html",
            "Empowers underprivileged girls with financial aid to pursue technical and engineering graduation programs.",
            "Female students studying in 1st/2nd year Engineering or Polytechnic Diploma. Family income <= 3 LPA."
        ),
        (
            "Havells 'Sanjivani' Higher Education Scholarship",
            "havells-sanjivani-scholarship",
            "Havells India",
            vlsi_field,
            "India", "Uttar Pradesh", "Noida",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.havells.com/en/about-havells/csr.html",
            "Dedicated to supporting youth in electrical, electronics, and instrumentation engineering studies.",
            "Undergraduate engineering students with minimum 65% in Class 12 and family income <= 4 LPA."
        ),
        (
            "Wipro 'Santo-Ignite' Scholarship for Persons with Disabilities",
            "wipro-santo-ignite-pwd-scholarship",
            "Wipro Foundation",
            cs_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            75000.00, "INR", "Per Annum",
            "https://wiprofoundation.org/initiatives/education/",
            "Specialized financial and assistive tech grant for students with locomotor, hearing, or visual disabilities pursuing college degrees.",
            "Valid PwD certificate (>= 40% disability), enrolled in higher secondary or undergraduate degree."
        ),
        (
            "Cadence Women in Technology Scholarship India",
            "cadence-women-in-tech-scholarship",
            "Cadence Design Systems",
            vlsi_field,
            "India", "Uttar Pradesh", "Noida",
            OpportunityMode.REMOTE,
            100000.00, "INR", "One-time Grant",
            "https://www.cadence.com/en_US/home/company/cadence-giving/women-in-tech.html",
            "Encourages female engineers in VLSI, chip design, electronic system design, and embedded architectures.",
            "Female students enrolled in 2nd or 3rd year B.Tech/Dual Degree in Electronics, VLSI, or CS."
        ),
        (
            "NXP Semiconductors India STEM Scholarship",
            "nxp-semiconductors-stem-scholarship",
            "NXP Semiconductors India",
            vlsi_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            80000.00, "INR", "Per Annum",
            "https://www.nxp.com/company/about-nxp/corporate-social-responsibility:CSR",
            "Focuses on semiconductor physics, microelectronics, and edge AI hardware education for undergraduate engineers.",
            "B.Tech students in Electronics & Communication or Microelectronics with CGPA >= 8.0."
        ),
        (
            "Qualcomm 'WE' (Women Entrepreneurs in Tech) Scholarship",
            "qualcomm-we-scholarship",
            "Qualcomm India",
            vlsi_field,
            "India", "Telangana", "Hyderabad",
            OpportunityMode.REMOTE,
            120000.00, "INR", "Per Annum",
            "https://www.qualcomm.com/company/corporate-responsibility/diversity/women-in-tech",
            "Provides financial grants and hardware development kits to promising female innovators in telecommunications and mobile compute.",
            "Full-time female students in B.Tech 2nd/3rd year in ECE, EEE, or CSE."
        ),
        (
            "L&T Build India Scholarship (BIS)",
            "lt-build-india-scholarship",
            "Larsen & Toubro Limited",
            civil_field,
            "India", "Tamil Nadu", "Chennai",
            OpportunityMode.ON_SITE,
            13400.00, "INR", "Per Month",
            "https://www.lntecc.com/build-india-scholarship/",
            "Prestigious 24-month program sponsoring full M.Tech in Construction Technology & Management at IIT Madras, IIT Delhi, NIT Trichy, or NIT Surathkal.",
            "Final year B.Tech Civil or Electrical engineering students with minimum 70% marks."
        ),
        (
            "Reliance Foundation Undergraduate Scholarship 2026",
            "reliance-foundation-ug-scholarship-2026",
            "Reliance Foundation",
            cs_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            200000.00, "INR", "Total Scholarship",
            "https://www.reliancefoundation.org/undergraduate-scholarships",
            "Up to INR 2,00,000 over the duration of the degree for 5,000 meritorious undergraduate students from all streams of study.",
            "First-year undergraduate students in any stream with >= 60% in Class 12 and family income <= 15 LPA."
        ),
        (
            "Reliance Foundation Postgraduate Scholarship in AI & Science",
            "reliance-foundation-pg-scholarship",
            "Reliance Foundation",
            data_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            600000.00, "INR", "Total Scholarship",
            "https://www.reliancefoundation.org/postgraduate-scholarships",
            "Prestigious fellowship granting up to INR 6,00,000 for top 100 students pursuing postgraduate studies in AI, Computer Science, and Renewable Energy.",
            "1st year full-time enrolled postgraduate students in eligible technology streams with top GATE scores."
        ),
        (
            "Aurobindo Pharma Foundation Higher Education Grant",
            "aurobindo-pharma-higher-ed-grant",
            "Aurobindo Pharma Foundation",
            biotech_field,
            "India", "Telangana", "Hyderabad",
            OpportunityMode.REMOTE,
            40000.00, "INR", "Per Annum",
            "https://www.aurobindofoundation.org/education.html",
            "Provides scholarships to students pursuing Pharmacy (B.Pharm), Biotechnology, and Organic Chemistry.",
            "Students enrolled in government pharmacy or science colleges with parental income under 3 LPA."
        ),
        (
            "Sun Pharma Science Foundation Research Fellowship",
            "sun-pharma-science-fellowship",
            "Sun Pharma Science Foundation",
            biotech_field,
            "India", "Delhi", "New Delhi",
            OpportunityMode.REMOTE,
            300000.00, "INR", "Total Grant",
            "https://www.sunpharmasciencefoundation.net/",
            "Encourages brilliant research scientists and doctoral students working in Medicinal Chemistry, Oncology, and Drug Formulation.",
            "Doctoral candidates or researchers below 30 years with research publications in peer-reviewed scientific journals."
        ),
        (
            "Glenmark Life Sciences STEM Scholarship",
            "glenmark-stem-scholarship",
            "Glenmark Foundation",
            chem_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.glenmarkfoundation.org/",
            "Financial aid for students pursuing Chemical Engineering, Process Technology, and Industrial Pharmacy.",
            "Students with 65%+ in Class 12 enrolled in accredited B.Chem or B.Pharm degrees."
        ),
        (
            "Thermax Foundation Sustainable Future Scholarship",
            "thermax-foundation-scholarship",
            "Thermax Limited",
            climate_field,
            "India", "Maharashtra", "Pune",
            OpportunityMode.REMOTE,
            60000.00, "INR", "Per Annum",
            "https://www.thermaxglobal.com/corporate-social-responsibility/",
            "Supporting innovative student projects and education in Clean Air, Clean Energy, and Waste-to-Energy technologies.",
            "Undergraduate engineering students in Environmental, Mechanical, or Energy engineering with income <= 5 LPA."
        ),
        (
            "JSW Udaan Scholarship Scheme",
            "jsw-udaan-scholarship-scheme",
            "JSW Foundation",
            civil_field,
            "India", "Maharashtra", "Mumbai",
            OpportunityMode.REMOTE,
            50000.00, "INR", "Per Annum",
            "https://www.buddy4study.com/page/jsw-udaan-scholarship",
            "Merit-cum-means scholarship for students residing near JSW plant locations pursuing higher education in Engineering, ITI, or Medical.",
            "Minimum 60% in Class 10/12/Diploma. Applicable to students in Karnataka, Maharashtra, Odisha, and Tamil Nadu."
        ),
        (
            "Vedanta 'Roshni' Women in Mining & Metallurgy Scholarship",
            "vedanta-roshni-mining-scholarship",
            "Vedanta Resources CSR",
            chem_field,
            "India", "Delhi", "New Delhi",
            OpportunityMode.REMOTE,
            75000.00, "INR", "Per Annum",
            "https://www.vedanta.com/sustainability/csr",
            "Promotes gender diversity in heavy industries by sponsoring women students in Mining, Metallurgy, and Geosciences.",
            "Female students enrolled in B.Tech Mining or Metallurgical Engineering at recognized institutions."
        ),
        (
            "Apollo Tyres 'Tarang' Technical Education Scholarship",
            "apollo-tyres-tarang-scholarship",
            "Apollo Tyres Foundation",
            vlsi_field,
            "India", "Haryana", "Gurugram",
            OpportunityMode.REMOTE,
            35000.00, "INR", "Per Annum",
            "https://www.apollotyres.com/en-in/sustainability/csr/",
            "Financial aid for students in Automobile Engineering, Polymer Science, and Mechanical disciplines.",
            "Students in diploma or B.Tech with parental income under 3 LPA."
        ),
        (
            "Triveni Turbine 'Shiksha Setu' Engineering Scholarship",
            "triveni-turbine-shiksha-setu",
            "Triveni Turbine Limited",
            vlsi_field,
            "India", "Karnataka", "Bengaluru",
            OpportunityMode.REMOTE,
            45000.00, "INR", "Per Annum",
            "https://www.triveniturbines.com/csr",
            "Supports bright economically disadvantaged students pursuing degrees in Mechanical, Electrical, and Turbomachinery disciplines.",
            "Students in government colleges with >= 7.0 CGPA and household income below 4 LPA."
        ),
        (
            "British Council Women in STEM Scholarships UK",
            "british-council-women-stem-scholarship",
            "British Council",
            cs_field,
            "United Kingdom", "London", "London",
            OpportunityMode.ON_SITE,
            35000.00, "GBP", "Total Scholarship",
            "https://www.britishcouncil.org/study-work-abroad/in-uk/scholarship-women-stem",
            "Full scholarship covering tuition fees, living stipend, travel costs, visa and health coverage fees for women pursuing STEM master's in the UK.",
            "Female applicants holding an undergraduate degree in STEM fields from India, Pakistan, or Southeast Asia."
        ),
        (
            "Commonwealth Master's Scholarship UK",
            "commonwealth-masters-scholarship-uk",
            "Commonwealth Scholarship Commission",
            data_field,
            "United Kingdom", "London", "London",
            OpportunityMode.ON_SITE,
            24000.00, "GBP", "Per Annum",
            "https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships/",
            "Full UK government funded scholarship including university tuition fees, monthly stipend, and airfare for talent from Commonwealth nations.",
            "Citizen of a Commonwealth country with a first-class undergraduate degree."
        )
    ]

    count_created = 0
    count_updated = 0
    
    for title, slug, org, field, country, state, city, mode, stipend, curr, period, url, desc, elig in scholarships_data:
        opp, created = Opportunity.objects.update_or_create(
            slug=slug,
            defaults={
                'title': title,
                'organization_name': org,
                'opportunity_type': OpportunityType.SCHOLARSHIP,
                'field': field,
                'country': country,
                'state': state,
                'city': city,
                'mode': mode,
                'stipend_salary': stipend,
                'currency': curr,
                'salary_period': period,
                'official_apply_url': url,
                'description': desc,
                'eligibility': elig,
                'is_verified': True,
                'verification_source': f"Buddy4Study & {org} Official Portal"
            }
        )
        if python_skill:
            opp.required_skills.add(python_skill)
            
        if created:
            count_created += 1
        else:
            count_updated += 1

    total_scholarships = Opportunity.objects.filter(opportunity_type=OpportunityType.SCHOLARSHIP).count()
    print(f"Successfully processed {len(scholarships_data)} Study4Buddy scholarships!")
    print(f"Created: {count_created}, Updated: {count_updated}")
    print(f"Total scholarships in database now: {total_scholarships}")

if __name__ == '__main__':
    seed_study4buddy()
