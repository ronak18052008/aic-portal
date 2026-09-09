import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from apps.taxonomy.models import Field, Subfield
from apps.education.models import Certification, CertificationLevel
from apps.skills.models import Skill

print("Seeding real subfields and certifications...")

# 1. SUBFIELDS SEEDING
subfields_by_field = {
    'computer-science': [
        ('Artificial Intelligence & Machine Learning', 'ai-ml', 'Deep learning, neural networks, computer vision, NLP and GenAI.'),
        ('Cloud Computing & Distributed Systems', 'cloud-distributed', 'Microservices architecture, distributed consensus, and serverless compute.'),
        ('Software Engineering & Web Architecture', 'software-web', 'Full-stack engineering, design patterns, scalable backend APIs.'),
        ('Cybersecurity & Cryptography', 'cyber-crypto', 'Zero trust architecture, ethical hacking, identity management and PKI.'),
        ('Data Engineering & Big Data', 'data-eng', 'Spark, distributed stream processing, data warehousing, and ETL pipelines.'),
    ],
    'cybersecurity-cloud': [
        ('Cloud Infrastructure & DevOps', 'cloud-devops', 'CI/CD pipelines, Kubernetes orchestration, infrastructure as code.'),
        ('Network Security & Defense', 'network-sec', 'Firewalls, intrusion detection, packet analysis, and VPN protocols.'),
        ('Application Security & DevSecOps', 'appsec-devsecops', 'Secure SDLC, SAST/DAST scanning, vulnerability remediation.'),
        ('Penetration Testing & Red Teaming', 'pen-testing', 'Offensive security operations, Metasploit, exploit analysis.'),
    ],
    'data-science': [
        ('Predictive Analytics & Statistical Modeling', 'predictive-analytics', 'Time series forecasting, regression models, hypothesis testing.'),
        ('Deep Learning & Neural Architectures', 'deep-learning-models', 'Transformers, CNNs, RNNs, and reinforcement learning.'),
        ('Business Intelligence & Visualization', 'bi-visualization', 'Tableau, PowerBI dashboards, operational metrics tracking.'),
        ('Natural Language Processing & Speech', 'nlp-speech', 'Text mining, sentiment analysis, speech-to-text models.'),
    ],
    'vlsi-semiconductors': [
        ('Digital ASIC & System-on-Chip (SoC)', 'digital-asic', 'Verilog/SystemVerilog RTL design, logic synthesis, and static timing analysis.'),
        ('Analog & Mixed-Signal IC Design', 'analog-ic', 'CMOS operational amplifiers, ADC/DAC converters, RF circuits.'),
        ('FPGA Prototyping & Reconfigurable Logic', 'fpga-prototyping', 'Xilinx/Altera FPGA synthesis, high-level synthesis (HLS).'),
        ('Embedded Systems & Microcontroller Firmware', 'embedded-firmware', 'ARM Cortex, RTOS, bare-metal C/C++, device drivers.'),
    ],
    'robotics-mechatronics': [
        ('Autonomous Mobile Robots & ROS', 'autonomous-ros', 'Robot Operating System, SLAM, path planning, lidar sensors.'),
        ('Industrial Automation & PLC', 'industrial-automation', 'SCADA systems, programmable logic controllers, industrial IoT.'),
        ('Drones & Unmanned Aerial Systems (UAS)', 'drones-uas', 'Autopilot systems, quadcopter dynamics, aerial mapping.'),
        ('Robotic Manipulation & Kinematics', 'robotic-manipulation', 'Forward and inverse kinematics, robotic arm trajectories.'),
    ],
    'business-fintech': [
        ('Algorithmic & Quantitative Trading', 'algo-trading', 'High-frequency trading strategies, portfolio optimization, quant risk.'),
        ('Blockchain, DeFi & Smart Contracts', 'blockchain-defi', 'Ethereum, Solidity, decentralized finance protocols, tokenomics.'),
        ('Digital Payments & Banking Architecture', 'digital-payments', 'UPI protocols, payment gateways, core banking APIs, PCI-DSS.'),
        ('Financial Analytics & Credit Scoring', 'fin-analytics', 'Credit risk assessment, fraud detection ML models, balance sheet analysis.'),
    ],
    'design-uiux': [
        ('User Research & Usability Testing', 'user-research', 'Interviews, heuristic evaluation, card sorting, user personas.'),
        ('Design Systems & Interactive Prototyping', 'design-systems', 'Figma components, atomic design systems, micro-interactions.'),
        ('Product Strategy & Design Operations', 'product-design-ops', 'Design metrics, cross-functional collaboration, UX audits.'),
    ],
    'biomedical-health': [
        ('Medical Imaging & AI Diagnostics', 'medical-imaging-ai', 'DICOM segmentation, pathology detection, MRI/CT classification.'),
        ('Health Informatics & EHR Systems', 'health-informatics', 'FHIR standards, electronic health record interoperability.'),
        ('Biomedical Instrumentation & Sensors', 'biomedical-sensors', 'ECG/EEG signal acquisition, wearable biosensors, telehealth.'),
    ],
    'genetics-biotech': [
        ('CRISPR & Genome Editing', 'crispr-editing', 'Cas9 gRNA design, targeted genomic integration, gene therapy.'),
        ('Bioinformatics & Sequence Analysis', 'bioinformatics-seq', 'Next-generation sequencing (NGS), BLAST, protein docking.'),
        ('Synthetic Biology & Bioprocessing', 'synthetic-biology', 'Metabolic engineering, microbial fermentation, bioreactors.'),
    ],
    'environment-climate': [
        ('Renewable Energy Systems (Solar & Wind)', 'renewable-solar-wind', 'Photovoltaic design, wind turbine aerodynamics, grid integration.'),
        ('Carbon Accounting & ESG Auditing', 'carbon-esg', 'GHG Protocol, Scope 1-3 emissions, corporate sustainability reporting.'),
        ('Climate Modeling & Remote Sensing', 'climate-remote-sensing', 'Satellite data analysis, GIS mapping, climate risk modeling.'),
    ],
    'mechanical-aerospace': [
        ('Computational Fluid Dynamics (CFD)', 'cfd-aerospace', 'Navier-Stokes solvers, boundary layer aerodynamics, wind tunnel testing.'),
        ('Finite Element Analysis (FEA) & Stress', 'fea-stress', 'Structural load testing, ANSYS modeling, fatigue failure analysis.'),
        ('Propulsion & Gas Turbine Systems', 'propulsion-turbines', 'Jet engines, rocket propulsion, thermodynamic combustion cycles.'),
    ],
    'civil-engineering': [
        ('Smart Infrastructure & Structural Design', 'smart-structures', 'Earthquake-resistant structures, Eurocode/IS-code analysis.'),
        ('Transportation & Highway Engineering', 'transport-engineering', 'Traffic simulation, pavement materials, smart tolling systems.'),
        ('Building Information Modeling (BIM)', 'bim-modeling', 'Revit 3D coordination, clash detection, 4D construction scheduling.'),
    ],
}

subfield_objs = {}
for fslug, sub_list in subfields_by_field.items():
    try:
        f = Field.objects.get(slug=fslug)
        for sname, sslug, sdesc in sub_list:
            sub, _ = Subfield.objects.get_or_create(
                field=f, slug=sslug,
                defaults={'name': sname, 'description': sdesc}
            )
            subfield_objs[sslug] = sub
    except Field.DoesNotExist:
        pass

print(f"Created/Verified {Subfield.objects.count()} subfields across fields.")

# 2. CERTIFICATIONS SEEDING (Real Industry Credentials)
certifications_data = [
    # AWS Certifications
    {
        'title': 'AWS Certified Solutions Architect - Associate',
        'slug': 'aws-certified-solutions-architect-associate',
        'issuing_organization': 'Amazon Web Services (AWS)',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'SAA-C03',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Validates ability to design and implement distributed systems on AWS, incorporating resilience, high performance, security, and cost optimization.',
        'exam_format': '65 Questions (Multiple Choice & Multiple Response), Proctored',
        'duration_minutes': 130,
        'validity_years': 3,
        'cost': 12500.00,
        'currency': 'INR',
        'skills': ['aws-cloud', 'docker', 'postgresql'],
        'official_verify_url': 'https://aws.amazon.com/certification/certified-solutions-architect-associate/',
        'verification_source': 'Amazon Web Services Global Certification Register',
    },
    {
        'title': 'AWS Certified Machine Learning - Specialty',
        'slug': 'aws-certified-machine-learning-specialty',
        'issuing_organization': 'Amazon Web Services (AWS)',
        'field_slug': 'computer-science',
        'subfield_slug': 'ai-ml',
        'credential_code': 'MLS-C01',
        'level': CertificationLevel.SPECIALTY,
        'description': 'Validates expertise in creating, training, tuning, and deploying machine learning (ML) models using AWS infrastructure.',
        'exam_format': '65 Questions, Proctored Online or Pearson VUE',
        'duration_minutes': 180,
        'validity_years': 3,
        'cost': 25000.00,
        'currency': 'INR',
        'skills': ['machine-learning', 'python', 'pytorch'],
        'official_verify_url': 'https://aws.amazon.com/certification/certified-machine-learning-specialty/',
        'verification_source': 'AWS Official Credential Directory',
    },

    # Google Cloud Certifications
    {
        'title': 'Google Cloud Professional Cloud Architect',
        'slug': 'gcp-professional-cloud-architect',
        'issuing_organization': 'Google Cloud',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'GCP-PCA',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Demonstrates proficiency in designing, developing, and managing robust, secure, scalable, highly available, and dynamic solutions on Google Cloud.',
        'exam_format': '50-60 Multiple Choice / Multiple Select questions, Proctored',
        'duration_minutes': 120,
        'validity_years': 2,
        'cost': 16500.00,
        'currency': 'INR',
        'skills': ['gcp-cloud', 'kubernetes', 'docker'],
        'official_verify_url': 'https://cloud.google.com/learn/certification/cloud-architect',
        'verification_source': 'Google Cloud Certified Directory',
    },
    {
        'title': 'Google Cloud Professional Data Engineer',
        'slug': 'gcp-professional-data-engineer',
        'issuing_organization': 'Google Cloud',
        'field_slug': 'data-science',
        'subfield_slug': 'data-eng',
        'credential_code': 'GCP-PDE',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Validates skills in building data-driven solutions by collecting, transforming, and publishing data with Google Cloud BigQuery, Dataflow, and Dataproc.',
        'exam_format': '50-60 Questions, Proctored',
        'duration_minutes': 120,
        'validity_years': 2,
        'cost': 16500.00,
        'currency': 'INR',
        'skills': ['gcp-cloud', 'postgresql', 'python'],
        'official_verify_url': 'https://cloud.google.com/learn/certification/data-engineer',
        'verification_source': 'Google Cloud Certified Directory',
    },

    # Microsoft Azure Certifications
    {
        'title': 'Microsoft Certified: Azure Solutions Architect Expert',
        'slug': 'microsoft-azure-solutions-architect-expert',
        'issuing_organization': 'Microsoft',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'AZ-305',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Validates subject matter expertise in designing cloud and hybrid solutions running on Microsoft Azure, covering compute, network, storage, and security.',
        'exam_format': '40-60 Questions including Case Studies, Proctored',
        'duration_minutes': 120,
        'validity_years': 1,
        'cost': 4800.00,
        'currency': 'INR',
        'skills': ['azure-cloud', 'network-security'],
        'official_verify_url': 'https://learn.microsoft.com/en-us/credentials/certifications/azure-solutions-architect/',
        'verification_source': 'Microsoft Learn Credential Verification',
    },
    {
        'title': 'Microsoft Certified: Azure Fundamentals',
        'slug': 'microsoft-azure-fundamentals-az900',
        'issuing_organization': 'Microsoft',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'AZ-900',
        'level': CertificationLevel.FOUNDATIONAL,
        'description': 'Demonstrates foundational level knowledge of cloud concepts and core Azure services, security, privacy, compliance, and trust.',
        'exam_format': '35-50 Questions, Proctored',
        'duration_minutes': 65,
        'validity_years': 99,
        'cost': 3696.00,
        'currency': 'INR',
        'skills': ['azure-cloud'],
        'official_verify_url': 'https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/',
        'verification_source': 'Microsoft Learn Credential Verification',
    },

    # Cisco Certifications
    {
        'title': 'Cisco Certified Network Associate (CCNA)',
        'slug': 'cisco-ccna-200-301',
        'issuing_organization': 'Cisco Systems',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'network-sec',
        'credential_code': 'CCNA 200-301',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Proves mastery in networking fundamentals, IP services, security fundamentals, automation, and programmability across enterprise networks.',
        'exam_format': '100-120 Questions with Simulation Labs, Proctored',
        'duration_minutes': 120,
        'validity_years': 3,
        'cost': 24500.00,
        'currency': 'INR',
        'skills': ['network-security', 'linux-admin'],
        'official_verify_url': 'https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html',
        'verification_source': 'Cisco Certified Professional Portal',
    },

    # Linux Foundation & CNCF
    {
        'title': 'Certified Kubernetes Administrator (CKA)',
        'slug': 'certified-kubernetes-administrator-cka',
        'issuing_organization': 'The Linux Foundation & CNCF',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'CKA',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Performance-based exam validating competence in Kubernetes cluster architecture, installation, configuration, networking, storage, and troubleshooting.',
        'exam_format': '100% Hands-on Practical Performance Exam (CLI based)',
        'duration_minutes': 120,
        'validity_years': 2,
        'cost': 32000.00,
        'currency': 'INR',
        'skills': ['kubernetes', 'docker', 'linux-admin'],
        'official_verify_url': 'https://www.cncf.io/certification/cka/',
        'verification_source': 'The Linux Foundation Certification Registry',
    },

    # CompTIA Security
    {
        'title': 'CompTIA Security+',
        'slug': 'comptia-security-plus-sy0-701',
        'issuing_organization': 'CompTIA',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'network-sec',
        'credential_code': 'SY0-701',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Global benchmark for foundational cybersecurity skills, assessing threats, attacks, vulnerabilities, architecture, and risk management.',
        'exam_format': 'Max 90 Questions (Performance-based & Multiple Choice)',
        'duration_minutes': 90,
        'validity_years': 3,
        'cost': 28000.00,
        'currency': 'INR',
        'skills': ['ethical-hacking', 'network-security'],
        'official_verify_url': 'https://www.comptia.org/certifications/security',
        'verification_source': 'CompTIA Career ID Verification',
    },

    # Project Management Institute (PMI)
    {
        'title': 'Project Management Professional (PMP)',
        'slug': 'project-management-professional-pmp',
        'issuing_organization': 'Project Management Institute (PMI)',
        'field_slug': 'tech-management',
        'subfield_slug': 'product-strategy',
        'credential_code': 'PMP',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Gold standard in project management certification, proving leadership and predictive, agile, and hybrid project delivery capability.',
        'exam_format': '180 Questions, 230 Minutes, Proctored Online or Center',
        'duration_minutes': 230,
        'validity_years': 3,
        'cost': 42000.00,
        'currency': 'INR',
        'skills': [],
        'official_verify_url': 'https://www.pmi.org/certifications/project-management-pmp',
        'verification_source': 'PMI Online Credential Registry',
    },

    # (ISC)²
    {
        'title': 'Certified Information Systems Security Professional (CISSP)',
        'slug': 'certified-information-systems-security-professional-cissp',
        'issuing_organization': '(ISC)²',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'network-sec',
        'credential_code': 'CISSP',
        'level': CertificationLevel.SPECIALTY,
        'description': 'Accelerates cybersecurity leadership careers by validating deep technical and managerial knowledge across 8 comprehensive cybersecurity domains.',
        'exam_format': 'CAT (Computerized Adaptive Testing) 100-150 Questions',
        'duration_minutes': 180,
        'validity_years': 3,
        'cost': 62000.00,
        'currency': 'INR',
        'skills': ['network-security', 'ethical-hacking'],
        'official_verify_url': 'https://www.isc2.org/certifications/cissp',
        'verification_source': '(ISC)² Member Verification Portal',
    },

    # NPTEL / IIT Madras National Certifications
    {
        'title': 'NPTEL Elite Certificate in Artificial Intelligence & Deep Learning',
        'slug': 'nptel-elite-ai-deep-learning',
        'issuing_organization': 'NPTEL & IIT Madras',
        'field_slug': 'computer-science',
        'subfield_slug': 'ai-ml',
        'credential_code': 'NPTEL-AI-2026',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Government of India recognized technical certificate issued by IIT Madras via SWAYAM-NPTEL with in-person proctored national exam.',
        'exam_format': 'In-Person Proctored Examination across 150+ Indian Cities',
        'duration_minutes': 180,
        'validity_years': 99,
        'cost': 1000.00,
        'currency': 'INR',
        'skills': ['python', 'pytorch', 'machine-learning'],
        'official_verify_url': 'https://nptel.ac.in/',
        'verification_source': 'SWAYAM-NPTEL National Database (MoE, Govt of India)',
    },
    {
        'title': 'NPTEL Elite+Gold in VLSI System Design & Verilog',
        'slug': 'nptel-elite-vlsi-system-design',
        'issuing_organization': 'NPTEL & IIT Kharagpur',
        'field_slug': 'vlsi-semiconductors',
        'subfield_slug': 'digital-asic',
        'credential_code': 'NPTEL-VLSI-2026',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'High-distinction hardware engineering certification assessing digital synthesis, CMOS design, and FPGA simulation.',
        'exam_format': 'In-Person National Proctored Examination',
        'duration_minutes': 180,
        'validity_years': 99,
        'cost': 1000.00,
        'currency': 'INR',
        'skills': ['vlsi-verilog', 'systemverilog', 'fpga-design'],
        'official_verify_url': 'https://nptel.ac.in/',
        'verification_source': 'SWAYAM-NPTEL National Database (MoE, Govt of India)',
    },

    # AICTE NEAT Certified Developer
    {
        'title': 'AICTE-NEAT Certified Python Fullstack Developer',
        'slug': 'aicte-neat-python-fullstack-dev',
        'issuing_organization': 'All India Council for Technical Education (AICTE)',
        'field_slug': 'computer-science',
        'subfield_slug': 'software-web',
        'credential_code': 'AICTE-NEAT-PFD',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'National Educational Alliance for Technology (NEAT) industry certification recognizing fullstack Python and Django capabilities.',
        'exam_format': 'Proctored Coding Assessment & Practical Project Evaluation',
        'duration_minutes': 120,
        'validity_years': 99,
        'cost': 1500.00,
        'currency': 'INR',
        'skills': ['python', 'django', 'postgresql'],
        'official_verify_url': 'https://neat.aicte-india.org/',
        'verification_source': 'AICTE NEAT Portal (Govt. of India)',
    },

    # Databricks
    {
        'title': 'Databricks Certified Data Engineer Associate',
        'slug': 'databricks-certified-data-engineer-associate',
        'issuing_organization': 'Databricks',
        'field_slug': 'data-science',
        'subfield_slug': 'data-eng',
        'credential_code': 'DB-DEA',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Demonstrates ability to use the Databricks Lakehouse Platform to complete data engineering tasks including Apache Spark and Delta Lake pipelines.',
        'exam_format': '45 Multiple Choice Questions, Proctored',
        'duration_minutes': 90,
        'validity_years': 2,
        'cost': 16500.00,
        'currency': 'INR',
        'skills': ['python', 'postgresql'],
        'official_verify_url': 'https://www.databricks.com/learn/certification/data-engineer-associate',
        'verification_source': 'Databricks Academy Registry',
    },

    # HashiCorp
    {
        'title': 'HashiCorp Certified: Terraform Associate',
        'slug': 'hashicorp-certified-terraform-associate',
        'issuing_organization': 'HashiCorp',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'TA-003',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Validates core infrastructure as code (IaC) concepts, Cloud architecture provisioning, and practical proficiency with HashiCorp Terraform.',
        'exam_format': '57 Questions (Multiple Choice & True/False), Proctored',
        'duration_minutes': 60,
        'validity_years': 2,
        'cost': 5800.00,
        'currency': 'INR',
        'skills': ['docker', 'aws-cloud'],
        'official_verify_url': 'https://www.hashicorp.com/certification/terraform-associate',
        'verification_source': 'HashiCorp Credly Badge Verification',
    },

    # Snowflake
    {
        'title': 'Snowflake SnowPro Core Certification',
        'slug': 'snowflake-snowpro-core-certification',
        'issuing_organization': 'Snowflake',
        'field_slug': 'data-science',
        'subfield_slug': 'data-eng',
        'credential_code': 'COF-C02',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Validates thorough knowledge of Snowflake Cloud Data Platform, Data loading, Data protection, scaling, and modern data architecture.',
        'exam_format': '100 Questions, Proctored Online',
        'duration_minutes': 115,
        'validity_years': 2,
        'cost': 14500.00,
        'currency': 'INR',
        'skills': ['postgresql'],
        'official_verify_url': 'https://www.snowflake.com/en/data-cloud/workloads/data-warehouse/certifications/snowpro-core/',
        'verification_source': 'Snowflake Credential Directory',
    },

    # Meta
    {
        'title': 'Meta Front-End Developer Professional Certificate',
        'slug': 'meta-front-end-developer-certificate',
        'issuing_organization': 'Meta Platforms',
        'field_slug': 'computer-science',
        'subfield_slug': 'software-web',
        'credential_code': 'META-FED',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Industry credential created by Meta software engineers, validating React.js, responsive UI, JavaScript ES6, and frontend performance.',
        'exam_format': 'Capstone Project Evaluation & Proctored Course Exams',
        'duration_minutes': 240,
        'validity_years': 99,
        'cost': 3500.00,
        'currency': 'INR',
        'skills': ['reactjs', 'typescript', 'nextjs'],
        'official_verify_url': 'https://www.coursera.org/professional-certificates/meta-front-end-developer',
        'verification_source': 'Meta Certified Digital Badge via Coursera',
    },

    # Harvard Online
    {
        'title': 'Harvard CS50 Verified Certificate of Completion',
        'slug': 'harvard-cs50-verified-certificate',
        'issuing_organization': 'Harvard University & edX',
        'field_slug': 'computer-science',
        'subfield_slug': 'software-web',
        'credential_code': 'CS50x',
        'level': CertificationLevel.FOUNDATIONAL,
        'description': 'Globally renowned computer science certificate taught by Prof. David J. Malan, verifying algorithmic thinking and software fundamentals in C and Python.',
        'exam_format': '10 Problem Sets & Final Software Project evaluated by Harvard TFs',
        'duration_minutes': 300,
        'validity_years': 99,
        'cost': 12500.00,
        'currency': 'INR',
        'skills': ['python', 'cpp-systems'],
        'official_verify_url': 'https://cs50.harvard.edu/x/',
        'verification_source': 'Harvard Division of Continuing Education',
    },

    # Stanford Online
    {
        'title': 'Stanford Online Machine Learning Professional Certificate',
        'slug': 'stanford-online-ml-certificate',
        'issuing_organization': 'Stanford Online & DeepLearning.AI',
        'field_slug': 'computer-science',
        'subfield_slug': 'ai-ml',
        'credential_code': 'STANFORD-MLS',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Mastery certificate from Stanford School of Engineering and Prof. Andrew Ng, covering modern machine learning, deep learning, and practical production AI.',
        'exam_format': 'Programming Assignments & Comprehensive Graded Assessments',
        'duration_minutes': 180,
        'validity_years': 99,
        'cost': 4500.00,
        'currency': 'INR',
        'skills': ['machine-learning', 'python', 'pytorch'],
        'official_verify_url': 'https://online.stanford.edu/courses/cs229-machine-learning',
        'verification_source': 'Stanford Center for Professional Development',
    },

    # OffSec
    {
        'title': 'Offensive Security Certified Professional (OSCP)',
        'slug': 'offensive-security-certified-professional-oscp',
        'issuing_organization': 'OffSec',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'network-sec',
        'credential_code': 'PEN-200 / OSCP',
        'level': CertificationLevel.SPECIALTY,
        'description': 'Renowned 24-hour hands-on penetration testing exam proving real-world persistence, exploit creation, and network defense compromise analysis.',
        'exam_format': '24-Hour Hands-On Live Lab Penetration Test + 24-Hour Documentation Report',
        'duration_minutes': 1440,
        'validity_years': 99,
        'cost': 125000.00,
        'currency': 'INR',
        'skills': ['ethical-hacking', 'network-security', 'linux-admin'],
        'official_verify_url': 'https://www.offsec.com/courses/pen-200/',
        'verification_source': 'OffSec Digital Credential Directory',
    },

    # CFA Institute
    {
        'title': 'Chartered Financial Analyst (CFA Level 1)',
        'slug': 'cfa-level-1-certification',
        'issuing_organization': 'CFA Institute',
        'field_slug': 'business-fintech',
        'subfield_slug': 'algo-trading',
        'credential_code': 'CFA-L1',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Global gold standard for investment analysis, portfolio management, ethical standards, financial reporting, and quantitative finance methods.',
        'exam_format': '180 Computer-Based Questions in 2 sessions of 135 mins each',
        'duration_minutes': 270,
        'validity_years': 99,
        'cost': 78000.00,
        'currency': 'INR',
        'skills': [],
        'official_verify_url': 'https://www.cfainstitute.org/en/programs/cfa',
        'verification_source': 'CFA Institute Global Member Directory',
    },

    # Scrum Alliance
    {
        'title': 'Certified ScrumMaster (CSM)',
        'slug': 'certified-scrum-master-csm',
        'issuing_organization': 'Scrum Alliance',
        'field_slug': 'tech-management',
        'subfield_slug': 'product-strategy',
        'credential_code': 'CSM',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Validates comprehension of Scrum values, team facilitation, sprint management, and Agile development lifecycle methodologies.',
        'exam_format': '50 Multiple Choice Questions, Proctored Online',
        'duration_minutes': 60,
        'validity_years': 2,
        'cost': 22000.00,
        'currency': 'INR',
        'skills': [],
        'official_verify_url': 'https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster',
        'verification_source': 'Scrum Alliance Certified Practitioner Directory',
    },

    # Red Hat
    {
        'title': 'Red Hat Certified System Administrator (RHCSA)',
        'slug': 'red-hat-certified-system-administrator-rhcsa',
        'issuing_organization': 'Red Hat',
        'field_slug': 'cybersecurity-cloud',
        'subfield_slug': 'cloud-infrastructure-devops',
        'credential_code': 'EX200',
        'level': CertificationLevel.ASSOCIATE,
        'description': 'Hands-on practical performance exam demonstrating core system administration skills required in Red Hat Enterprise Linux environments.',
        'exam_format': '100% Hands-On Practical Lab Exam',
        'duration_minutes': 180,
        'validity_years': 3,
        'cost': 21000.00,
        'currency': 'INR',
        'skills': ['linux-admin'],
        'official_verify_url': 'https://www.redhat.com/en/services/certification/rhcsa',
        'verification_source': 'Red Hat Certification Central Registry',
    },

    # Oracle
    {
        'title': 'Oracle Certified Professional: Java SE 17 Developer',
        'slug': 'oracle-certified-professional-java-se-17',
        'issuing_organization': 'Oracle Corporation',
        'field_slug': 'computer-science',
        'subfield_slug': 'software-web',
        'credential_code': '1Z0-829',
        'level': CertificationLevel.PROFESSIONAL,
        'description': 'Validates deep proficiency in Java SE 17, covering object-oriented programming, concurrency, stream APIs, lambda expressions, and modular systems.',
        'exam_format': '50 Multiple Choice Questions, Proctored Online',
        'duration_minutes': 90,
        'validity_years': 99,
        'cost': 18500.00,
        'currency': 'INR',
        'skills': ['java-springboot'],
        'official_verify_url': 'https://education.oracle.com/java-se-17-developer/pexam_1Z0-829',
        'verification_source': 'Oracle CertView Online Verification',
    }
]

created_count = 0
for cdata in certifications_data:
    try:
        f = Field.objects.get(slug=cdata['field_slug'])
    except Field.DoesNotExist:
        f = Field.objects.first()

    sub = subfield_objs.get(cdata['subfield_slug'])

    cert, created = Certification.objects.get_or_create(
        slug=cdata['slug'],
        defaults={
            'title': cdata['title'],
            'issuing_organization': cdata['issuing_organization'],
            'field': f,
            'subfield': sub,
            'credential_code': cdata['credential_code'],
            'level': cdata['level'],
            'description': cdata['description'],
            'exam_format': cdata['exam_format'],
            'duration_minutes': cdata['duration_minutes'],
            'validity_years': cdata['validity_years'],
            'cost': cdata['cost'],
            'currency': cdata['currency'],
            'official_verify_url': cdata['official_verify_url'],
            'is_verified': True,
            'verification_source': cdata['verification_source']
        }
    )
    # Add skills
    for s_slug in cdata['skills']:
        try:
            sk = Skill.objects.get(slug=s_slug)
            cert.skills_covered.add(sk)
        except Skill.DoesNotExist:
            pass
    if created:
        created_count += 1

print(f"Seeded {created_count} new certifications. Total certifications now: {Certification.objects.count()}")
