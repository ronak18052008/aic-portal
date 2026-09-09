from django.core.management.base import BaseCommand
from apps.accounts.models import User, PrimaryRole, SubRole
from apps.taxonomy.models import Field
from apps.skills.models import Skill, UserSkill, SkillProficiency, SkillEvidence, Assessment, Question, AssessmentType
from apps.education.models import Course, ModeType
from apps.opportunities.models import Opportunity, OpportunityType, OpportunityMode
from apps.institutions.models import Institution

class Command(BaseCommand):
    help = 'Seed Faculty Skills, FDPs, Real Industry Collaborations, and Adaptive Skill Tests'

    def handle(self, *args, **options):
        self.stdout.write("1. Seeding Faculty Skills & Specializations for Academician...")
        prof_user = User.objects.filter(email='prof@aic.com').first()
        cs_field = Field.objects.filter(slug='computer-science').first() or Field.objects.first()
        data_field = Field.objects.filter(slug='data-science').first() or cs_field
        cloud_field = Field.objects.filter(slug='cybersecurity-cloud').first() or cs_field

        faculty_skills_data = [
            ('Deep Learning & Transformer Architectures', 'computer-science', SkillProficiency.EXPERT, 98),
            ('Computer Science & AI Curriculum Design', 'computer-science', SkillProficiency.EXPERT, 96),
            ('Distributed Cloud Systems & SRE', 'cybersecurity-cloud', SkillProficiency.ADVANCED, 92),
            ('Research Grant Proposal & Publication', 'computer-science', SkillProficiency.EXPERT, 95),
            ('AI Ethics & High-Assurance Computing', 'computer-science', SkillProficiency.ADVANCED, 90),
            ('High-Performance GPU Cluster Computing', 'computer-science', SkillProficiency.ADVANCED, 93),
        ]

        for sname, fslug, prof_level, score in faculty_skills_data:
            field_obj = Field.objects.filter(slug=fslug).first() or cs_field
            skill, _ = Skill.objects.get_or_create(
                name=sname,
                defaults={
                    'slug': sname.lower().replace(' ', '-').replace('&', 'and').replace('(', '').replace(')', ''),
                    'field': field_obj,
                    'category': 'Faculty Research & Academic Specialization',
                    'industry_demand_score': 95
                }
            )
            if prof_user:
                UserSkill.objects.update_or_create(
                    user=prof_user,
                    skill=skill,
                    defaults={
                        'proficiency': prof_level,
                        'evidence_type': SkillEvidence.MENTOR_VERIFIED,
                        'score_percentage': score,
                        'verified_by': 'National Board of Higher Education & AICTE'
                    }
                )

        self.stdout.write("2. Seeding Real Faculty Development Programmes (FDP)...")
        fdp_courses = [
            (
                'AICTE ATAL National FDP on Generative AI & Foundation Models',
                'fdp-aicte-genai-2026',
                'AICTE & IIT Bombay ATAL Academy',
                cs_field,
                'Prof. Pushpak Bhattacharyya',
                'National Faculty Development Programme designed for engineering professors and educators to integrate Large Language Models, Prompt Engineering, and RAG into computer science curricula.',
                'Advanced Faculty',
                60,
                0.00,
                'https://www.aicte-india.org/atal',
                4.9
            ),
            (
                'NPTEL FDP on High-Performance Computing & GPU Acceleration',
                'fdp-nptel-hpc-gpu',
                'IIT Madras & NPTEL',
                cs_field,
                'Prof. Rupesh Nasre',
                'Pedagogical and hands-on training for faculty on multi-threaded CUDA architectures, OpenMP, and distributed GPU cluster computing for academic research laboratories.',
                'Advanced Faculty',
                80,
                0.00,
                'https://nptel.ac.in/courses',
                4.8
            ),
            (
                'Microsoft Academic Cloud Excellence: DevOps & SRE for Educators',
                'fdp-msft-cloud-devops',
                'Microsoft Educator Programs',
                cloud_field,
                'Dr. Sarah Jenkins & Microsoft Cloud Team',
                'Educator enablement program covering cloud-native microservices, containerization with Kubernetes, CI/CD automation, and modern infrastructure labs for college departments.',
                'Professional Educator',
                50,
                0.00,
                'https://learn.microsoft.com/en-us/training/educator-center/',
                4.9
            ),
            (
                'NVIDIA DLI Educator Workshop: Multi-Modal AI & Robotics Labs',
                'fdp-nvidia-dli-robotics',
                'NVIDIA Deep Learning Institute',
                cs_field,
                'NVIDIA AI Academic Specialists',
                'Official instructor-led certification equipping professors with classroom-ready course kits in computer vision, robotics simulation, and accelerated tensor computing.',
                'Specialty Educator',
                40,
                0.00,
                'https://www.nvidia.com/en-us/training/educators/',
                5.0
            ),
            (
                'IISc National FDP on Quantum Information Theory & Algorithms',
                'fdp-iisc-quantum-theory',
                'IISc Bengaluru & DST Quantum Mission',
                cs_field,
                'Prof. Arindam Ghosh',
                'Faculty empowerment program covering quantum circuits, Qiskit simulations, quantum error correction, and establishing undergraduate quantum computing electives.',
                'Advanced Faculty',
                60,
                0.00,
                'https://iisc.ac.in/',
                4.9
            ),
            (
                'IIT Delhi FDP on Embedded Systems & RISC-V Microarchitecture',
                'fdp-iitd-riscv-embedded',
                'IIT Delhi Department of Computer Science',
                cs_field,
                'Prof. M. Balakrishnan',
                'Comprehensive course for faculty to modernize microprocessors curriculum using open-source RISC-V cores, FPGA synthesis, and real-time operating systems.',
                'Advanced Faculty',
                55,
                0.00,
                'https://home.iitd.ac.in/',
                4.8
            )
        ]

        for title, slug, provider, fld, instr, desc, lvl, dur, price, url, rating in fdp_courses:
            Course.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'provider': provider,
                    'field': fld,
                    'instructor': instr,
                    'description': desc,
                    'level_name': lvl,
                    'duration_hours': dur,
                    'mode': ModeType.ONLINE,
                    'price': price,
                    'currency': 'INR',
                    'provides_certificate': True,
                    'rating': rating,
                    'official_url': url,
                    'is_verified': True
                }
            )

        self.stdout.write("3. Seeding Real Industry Collaboration Projects & Grants...")
        industry_collabs = [
            (
                'Google DeepMind Foundation Models Research Grant',
                'collab-deepmind-llm-grant',
                'Google DeepMind India',
                cs_field,
                'India', 'Karnataka', 'Bengaluru',
                OpportunityMode.HYBRID,
                4500000.00, 'INR', 'Total Grant',
                'Joint academia-industry collaborative research on alignment, multi-modal reasoning, and formal verification of agentic AI models. Open for university faculty and doctoral candidates.',
                'https://deepmind.google/about/careers/'
            ),
            (
                'NVIDIA Accelerated Computing & Robotics Joint Lab',
                'collab-nvidia-robotics-lab',
                'NVIDIA Technology Center',
                cs_field,
                'India', 'Telangana', 'Hyderabad',
                OpportunityMode.HYBRID,
                8000000.00, 'INR', 'Hardware & Cloud Credits',
                'Industry collaboration providing high-performance DGX GPU clusters, Isaac Sim platforms, and research funding for university robotics and edge perception laboratories.',
                'https://www.nvidia.com/en-in/about-nvidia/careers/'
            ),
            (
                'Microsoft Azure Clean Energy & Sustainable Cloud Consortium',
                'collab-msft-clean-cloud',
                'Microsoft Research India',
                cloud_field,
                'India', 'Karnataka', 'Bengaluru',
                OpportunityMode.HYBRID,
                6000000.00, 'INR', 'Research Funding',
                'Multi-institution collaborative grant researching green datacenter optimization, AI-driven workload scheduling, and zero-carbon grid balancing with academic partners.',
                'https://www.microsoft.com/en-us/research/'
            ),
            (
                'Pfizer-Novartis AI-Driven Drug Discovery Academic Alliance',
                'collab-pharma-ai-drug',
                'Novartis & Pfizer Global R&D',
                cs_field,
                'India', 'Telangana', 'Hyderabad',
                OpportunityMode.HYBRID,
                9500000.00, 'INR', 'Annual Grant',
                'Consortium research grant focusing on graph neural networks, generative molecular design, and cryogenic electron microscopy structure analysis with chemistry and biomedical departments.',
                'https://www.novartis.com/careers'
            ),
            (
                'ISRO Space Technology Cell: Fault-Tolerant Satellite Computing',
                'collab-isro-space-payload',
                'Indian Space Research Organisation (ISRO)',
                cs_field,
                'India', 'Karnataka', 'Bengaluru',
                OpportunityMode.ON_SITE,
                12000000.00, 'INR', 'Sponsored Research Grant',
                'Sponsored space research partnership for developing radiation-hardened processor architectures, autonomous orbital navigation, and high-throughput telemetry.',
                'https://www.isro.gov.in/Respond.html'
            ),
            (
                'Tata Motors Next-Gen EV Battery Analytics & Digital Twin',
                'collab-tatamotors-ev-battery',
                'Tata Motors Technology Center',
                cs_field,
                'India', 'Maharashtra', 'Pune',
                OpportunityMode.HYBRID,
                5000000.00, 'INR', 'Research Grant',
                'Joint university research project analyzing lithium battery degradation models, physics-informed neural networks for thermal runaway prediction, and regenerative power systems.',
                'https://www.tatamotors.com/careers/'
            ),
            (
                'Qualcomm 6G Wireless & Edge Intelligence Project',
                'collab-qualcomm-6g-edge',
                'Qualcomm Research India',
                cs_field,
                'India', 'Telangana', 'Hyderabad',
                OpportunityMode.HYBRID,
                7500000.00, 'INR', 'Research Grant',
                'Collaborative research initiative investigating sub-terahertz communications, ultra-low latency semantic beamforming, and on-device neuromorphic processing.',
                'https://www.qualcomm.com/company/careers'
            )
        ]

        for title, slug, org, fld, country, state, city, mode, sal, curr, period, desc, url in industry_collabs:
            Opportunity.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'organization_name': org,
                    'opportunity_type': OpportunityType.PROJECT,
                    'field': fld,
                    'country': country,
                    'state': state,
                    'city': city,
                    'mode': mode,
                    'stipend_salary': sal,
                    'currency': curr,
                    'salary_period': period,
                    'description': desc,
                    'official_apply_url': url,
                    'is_verified': True,
                    'verification_source': f'{org} Academic Partnerships Board'
                }
            )

        self.stdout.write("4. Seeding Adaptive Assessments & MCQ Questions...")
        assessments_data = [
            (
                'Python Programming Mastery Assessment',
                'Python Programming',
                'computer-science',
                AssessmentType.TECHNICAL,
                25, 5, 70,
                [
                    (
                        'What is the time complexity of searching an element in a Python dictionary on average?',
                        'O(n)', 'O(1)', 'O(log n)', 'O(n log n)',
                        'B',
                        'Python dictionaries are implemented using hash tables, which achieve O(1) average-case time complexity for key lookups.'
                    ),
                    (
                        'What does the `@property` decorator in Python accomplish?',
                        'Defines a class-level static method',
                        'Allows a method to be accessed like an attribute while providing getter and setter control',
                        'Protects a variable from being garbage collected',
                        'Forces the method to execute asynchronously',
                        'B',
                        'The @property decorator allows methods to be accessed as attributes with encapsulation and validation.'
                    ),
                    (
                        'Which Python construct is used to create a generator function that produces items lazily?',
                        'return', 'yield', 'produce', 'emit',
                        'B',
                        'The yield statement turns a regular function into a generator that computes values on demand with minimal memory footprint.'
                    ),
                    (
                        'How does the Global Interpreter Lock (GIL) affect multi-threaded CPU-bound programs in CPython?',
                        'It allows full parallel CPU utilization across all cores',
                        'It prevents multiple native threads from executing Python bytecode simultaneously',
                        'It automatically compiles Python bytecode to C code at runtime',
                        'It restricts network socket connections to a single port',
                        'B',
                        'CPython\'s GIL ensures only one thread executes Python bytecode at a time, making multiprocessing necessary for CPU-bound tasks.'
                    ),
                    (
                        'In Python, which built-in function returns an iterator of tuples containing the index and value of an iterable?',
                        'zip()', 'enumerate()', 'range()', 'map()',
                        'B',
                        'enumerate() takes an iterable and returns an enumerate object yielding (index, item) pairs.'
                    )
                ]
            ),
            (
                'PyTorch & Deep Learning Systems Assessment',
                'PyTorch Deep Learning',
                'computer-science',
                AssessmentType.TECHNICAL,
                30, 5, 70,
                [
                    (
                        'In PyTorch, what method is called on a scalar loss tensor to compute gradients of all leaf tensors?',
                        'loss.backward()', 'loss.forward()', 'loss.step()', 'loss.zero_grad()',
                        'A',
                        'Calling loss.backward() triggers the autograd dynamic computation graph backward pass.'
                    ),
                    (
                        'Why must `optimizer.zero_grad()` be executed before computing gradients in a training loop?',
                        'PyTorch accumulates gradients on successive backward passes by default',
                        'It frees GPU memory allocated for weights',
                        'It initializes the learning rate scheduler',
                        'It prevents numerical overflow in cross-entropy loss',
                        'A',
                        'PyTorch accumulates gradients in tensor.grad fields, so zero_grad() is required to reset them per iteration.'
                    ),
                    (
                        'Which attention mechanism allows Transformer models to process sequences in parallel during training?',
                        'Recurrent Hidden States', 'Multi-Head Self-Attention', 'Convolutional Pooling', 'Skip-gram Embedding',
                        'B',
                        'Multi-Head Self-Attention calculates pairwise attention weights across all sequence tokens simultaneously.'
                    ),
                    (
                        'What is the purpose of `model.eval()` before running inference on a PyTorch model?',
                        'Disables backpropagation and frees all parameters',
                        'Sets dropout and batch normalization layers to evaluation mode',
                        'Quantizes float32 weights to int8 format',
                        'Compiles the model into TorchScript C++ binary',
                        'B',
                        'model.eval() switches layers like Dropout (deactivated) and BatchNorm (using running statistics) to evaluation mode.'
                    ),
                    (
                        'Which technique is used to train large neural networks when parameters exceed a single GPU memory capacity?',
                        'Data Parallelism (DP)', 'Fully Sharded Data Parallel (FSDP) / Model Parallelism', 'SGD with Momentum', 'Dropout Normalization',
                        'B',
                        'FSDP shards model parameters, gradients, and optimizer states across multiple GPUs to fit massive LLMs.'
                    )
                ]
            ),
            (
                'Django Enterprise Web Architecture Assessment',
                'Django Web Framework',
                'computer-science',
                AssessmentType.TECHNICAL,
                25, 5, 70,
                [
                    (
                        'Which Django ORM method is used to mitigate the N+1 database query problem on ForeignKey relationships?',
                        'prefetch_related()', 'select_related()', 'distinct()', 'values_list()',
                        'B',
                        'select_related() performs an SQL JOIN to fetch single-valued ForeignKey relationships in a single database query.'
                    ),
                    (
                        'In Django middleware, what does returning an HttpResponse from `process_request` cause?',
                        'It terminates the request and immediately returns the response, skipping view processing',
                        'It logs an unhandled exception to stdout',
                        'It restarts the Django ASGI worker',
                        'It executes all remaining middlewares in reverse order',
                        'A',
                        'Short-circuiting in middleware returns the response immediately without invoking the downstream view.'
                    ),
                    (
                        'Where should complex business logic and state transitions be encapsulated according to Django best practices?',
                        'Template tags', 'Model methods, Managers, or Service Layer classes', 'URLs configuration', 'Context processors',
                        'B',
                        'Fat models, custom QuerySets/Managers, or service layers maintain clean separation of concerns.'
                    ),
                    (
                        'How does Django protect against Cross-Site Request Forgery (CSRF) on POST requests?',
                        'By encrypting the entire HTTP payload with TLS',
                        'By validating a unique cryptographically signed session token included in the form',
                        'By blocking all incoming requests from non-localhost IP addresses',
                        'By converting all POST requests into idempotent GET requests',
                        'B',
                        'Django uses a unique CSRF token cookie matched against a hidden POST parameter to block cross-origin submissions.'
                    ),
                    (
                        'Which Django command safely applies database schema alterations in production?',
                        'python manage.py inspectdb', 'python manage.py migrate', 'python manage.py syncdb', 'python manage.py flush',
                        'B',
                        'manage.py migrate safely transitions the database schema according to compiled migration files.'
                    )
                ]
            ),
            (
                'Cloud Architecture & Docker Containers Assessment',
                'Docker Containerization',
                'cybersecurity-cloud',
                AssessmentType.TECHNICAL,
                25, 5, 70,
                [
                    (
                        'What Linux kernel technology provides isolation of processes, network interfaces, and mounts in Docker?',
                        'Kernel Modules', 'Namespaces and Control Groups (cgroups)', 'VirtualBox Hypervisor', 'Sysfs and Udev',
                        'B',
                        'Namespaces provide resource isolation, while cgroups enforce resource metering and limits.'
                    ),
                    (
                        'In multi-stage Docker builds, what is the primary architectural benefit?',
                        'Allows running multiple operating systems concurrently in one container',
                        'Significantly reduces final container image size by discarding build tools and intermediate artifacts',
                        'Encrypts container filesystems at rest',
                        'Automatically scales Docker containers on Kubernetes',
                        'B',
                        'Multi-stage builds separate the compilation environment from the lean runtime image.'
                    ),
                    (
                        'In Kubernetes, which controller ensures a specified number of identical pod replicas are running at all times?',
                        'Ingress Controller', 'ReplicaSet / Deployment Controller', 'DaemonSet', 'Job Controller',
                        'B',
                        'Deployments manage ReplicaSets to maintain the declared desired replica count.'
                    ),
                    (
                        'Which HTTP header is utilized by Reverse Proxies (e.g. Nginx) to forward the client original IP address to containers?',
                        'Host', 'X-Forwarded-For', 'Authorization', 'Content-Encoding',
                        'B',
                        'X-Forwarded-For preserves the real client IP address through proxy hops.'
                    ),
                    (
                        'What is the function of a Kubernetes Service of type `ClusterIP`?',
                        'Exposes the service externally via a cloud load balancer',
                        'Provides an internal stable IP address and DNS name accessible only within the cluster',
                        'Allocates a static public IP address to every worker node',
                        'Mounts persistent storage volumes to pods',
                        'B',
                        'ClusterIP is the default internal service type providing stable east-west cluster communication.'
                    )
                ]
            ),
            (
                'Data Science & SQL Analytics Assessment',
                'SQL Advanced Query Optimization',
                'data-science',
                AssessmentType.TECHNICAL,
                25, 5, 70,
                [
                    (
                        'What is the difference between `RANK()` and `DENSE_RANK()` window functions in SQL?',
                        'RANK() leaves gaps in ranking order when ties occur, while DENSE_RANK() does not',
                        'DENSE_RANK() only works on string data types',
                        'RANK() requires an aggregation GROUP BY clause',
                        'DENSE_RANK() sorts values in descending order only',
                        'A',
                        'RANK() skips ranking numbers after ties (e.g., 1, 1, 3), whereas DENSE_RANK() produces consecutive ranks (1, 1, 2).'
                    ),
                    (
                        'Which SQL index type is optimal for high-cardinality columns frequently queried with range operators (e.g., BETWEEN, <, >)?',
                        'Hash Index', 'B-Tree Index', 'Bitmap Index', 'Spatial Index',
                        'B',
                        'B-Tree indices maintain sorted key structures ideal for range scans and exact lookups.'
                    ),
                    (
                        'In relational algebra, what happens during an `INNER JOIN` between two tables with non-matching rows?',
                        'All unmatched rows from both tables are retained with NULLs',
                        'Only rows that satisfy the join predicate in both tables are returned',
                        'The Cartesian product of both tables is returned',
                        'An exception is raised by the query planner',
                        'B',
                        'INNER JOIN strictly filters for records that satisfy matching keys in both participating relations.'
                    ),
                    (
                        'In Pandas, which method computes summary statistics including count, mean, std, and percentiles for numerical columns?',
                        'df.info()', 'df.describe()', 'df.summary()', 'df.aggregate()',
                        'B',
                        'df.describe() generates comprehensive descriptive statistics of DataFrame numerical series.'
                    ),
                    (
                        'What metric is most appropriate for evaluating a binary classification model on an imbalanced dataset where the positive class is rare?',
                        'Accuracy', 'ROC-AUC and Precision-Recall F1-Score', 'Mean Squared Error (MSE)', 'R-Squared Score',
                        'B',
                        'Accuracy is misleading on imbalanced datasets; Precision-Recall AUC and F1 provide honest evaluation of the minority class.'
                    )
                ]
            )
        ]

        for title, skill_name, field_slug, atype, dur, total_q, pass_m, questions in assessments_data:
            fld = Field.objects.filter(slug=field_slug).first() or cs_field
            skill, _ = Skill.objects.get_or_create(
                name=skill_name,
                defaults={
                    'slug': skill_name.lower().replace(' ', '-').replace('&', 'and'),
                    'field': fld,
                    'category': 'Technical Competency'
                }
            )
            assessment, _ = Assessment.objects.update_or_create(
                title=title,
                defaults={
                    'assessment_type': atype,
                    'skill': skill,
                    'duration_minutes': dur,
                    'total_questions': total_q,
                    'pass_mark': pass_m
                }
            )
            assessment.questions.all().delete()
            for qtext, oa, ob, oc, od, corr, expl in questions:
                Question.objects.create(
                    assessment=assessment,
                    question_text=qtext,
                    option_a=oa,
                    option_b=ob,
                    option_c=oc,
                    option_d=od,
                    correct_option=corr,
                    explanation=expl,
                    difficulty='MEDIUM'
                )

        self.stdout.write(self.style.SUCCESS("All Faculty Skills, FDPs, Industry Collaborations, and Adaptive Assessments successfully seeded!"))
