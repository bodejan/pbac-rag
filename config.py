import logging

DB_CONTEXT = "The dataset contains detailed records of medical visits from multiple patients, including information about symptoms, diagnoses, treatments, and patient demographics. Each record also includes specific details such as the consulting physician, patient consent for treatments, emergency contacts, and the intended purposes of the medical data."

DB_DIALECT = "MongoDB"

DB_COLLECTION_INFO = """The collection contains documents representing individual patient visits. 
Each document follows a specific schema with multiple fields keys representing various attributes of the visit, patient, diagnosis, and treatment information. 
Except for the ReferenceID field, all other fields have associated intended purposes (IP) that specify the allowed uses of the data.
All documents in the collection follow the same schema and have the following keys:
 - ReferenceID: Unique reference ID for the medical record
 - ReportYear (INTEGER): Year of the medical report: '2001' to '2024'
 - DiagnosisCategory: Primary diagnosis category: 'Orth/Musculoskeletal', 'Mental Disorder', 'Cancer', 'CNS/ Neuromusc Dis', 'Endocrine/Metabolic', 'Cardiac/Circ Problem', 'Infectious Disease', 'Digestive System/ GI', 'Autism Spectrum', 'Skin Disorders', 'OB-GYN/ Pregnancy', 'Pediatrics', 'Morbid Obesity', 'Respiratory System', 'GU/ Kidney Disorder', 'Immuno Disorders', 'Prevention/Good Hlth', 'Ears/Nose/Throat', 'Vision', 'Foot Disorder', 'Trauma/ Injuries', 'Genetic Diseases', 'Chron Pain Synd', 'Blood Related Disord', 'Dental Problems', 'Not Applicable', 'Post Surgical Comp', 'Pregnancy/Childbirth', 'Other'
 - DiagnosisSubCategory: Sub-category of the diagnosis, 418 distinct values. The most common include: 'Other', 'Hepatitis', 'Back Pain', 'Osteoarthritis', 'Not Applicable'
 - TreatmentCategory: Primary treatment category: 'Pharmacy', 'Diag Imag & Screen', 'Mental Health', 'DME', 'Orthopedic Proc', 'Pain Management', 'Cancer Care', 'Gen Surg Proc', 'Rehab/ Svc - Outpt', 'Reconstr/Plast Proc', 'Elect/Therm/Radfreq', 'Autism Related Tx', 'Diag/ MD Eval', 'Emergency/Urg Care', 'Rehab/Svcs SNF Inpt', 'Special Proc', 'Cardio-Vasc Proc', 'Alternative Tx', 'Ear-Nose-Thro Proc', 'Acute Med Svc Inpt', 'Ob-Gyn Proc', 'Dent/Orthodont Proc', 'Chiropractic Care', 'Neurosurgery Proc', 'Home Health Care', 'Vision Services', 'Urology Proc', 'Ophthalmology Proc', 'Transportation', 'Vision Services/Ophthalmology', 'Prev Health Screen', 'Not Applicable', 'MLTSS', 'Gen Surg proc'
 - TreatmentSubCategory: Sub-category of the treatment, 381 distinct values. The most common include: 'Other', 'Anti-virals', 'RTC/ Admit', 'Speech Therapy'
 - Determination: Indicates if the determination was upheld or overturned: 'Overturned Decision of Health Plan', 'Upheld Decision of Health Plan'
 - Type: Type of treatment administered: 'Medical Necessity', 'Experimental/Investigational', 'Urgent Care'
 - AgeRange: Age range of the patient: '0 to 10', '11 to 20', '21 to 30', '31 to 40', '41 to 50', '51 to 64', '65+'
 - PatientGender: Gender of the patient: 'Female', 'Male', 'Other'
 - Findings: Text containing findings from the medical examination.
 - PatientName: Full name of the patient
 - PatientAge (INTEGER): Age of the patient
 - PatientPhone: US phone number of the patient, e.g., '+1-346-618-8073'
 - PatientAddress: Address of the patient
 - PatientBloodType: Blood type of the patient: 'A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-'
 - PatientSSN: Social Security Number of the patient, format: 'XXX-XX-XXXX'
 - PatientInsuranceProvider: Insurance provider of the patient: 'CVS Health (Aetna)', 'Medicare', 'Highmark', 'UnitedHealth Group', 'Molina Healthcare', 'Centene Corporation', 'Medicaid', 'Blue Cross Blue Shield', 'Kaiser Foundation', 'Anthem Inc.', 'Independence Health Group', 'WellCare', 'Cigna Health', 'GuideWell Mutual Holding', 'Humana', 'HCSC (Health Care Service Corporation)'
 - PatientInsuranceNumber: Insurance number of the patient
 - ConsultingPhysician: Physician who consulted on the case: 'Dr. Jerry Daniels', 'Dr. Eddie Young', 'Dr. Michelle Lamb', 'Dr. Shelly Hunt', 'Dr. Alexandria Gaines', 'Dr. James Barber'
 - ReportYear_IP: List of intended purposes (IP) for the ReportYear field.
 - DiagnosisCategory_IP: List of intended purposes (IP) for the DiagnosisCategory field.
 - DiagnosisSubCategory_IP: List of intended purposes (IP) for the DiagnosisSubCategory field.
 - TreatmentCategory_IP: List of intended purposes (IP) for the TreatmentCategory field.
 - TreatmentSubCategory_IP: List of intended purposes (IP) for the TreatmentSubCategory field.
 - Determination_IP: List of intended purposes (IP) for the Determination field.
 - Type_IP: List of intended purposes (IP) for the Type field.
 - AgeRange_IP: List of intended purposes (IP) for the AgeRange field.
 - PatientGender_IP: List of intended purposes (IP) for the PatientGender field.
 - Findings_IP: List of intended purposes (IP) for the Findings field.
 - PatientName_IP: List of intended purposes (IP) for the PatientName field.
 - PatientAge_IP: List of intended purposes (IP) for the PatientAge field.
 - PatientPhone_IP: List of intended purposes (IP) for the PatientPhone field.
 - PatientAddress_IP: List of intended purposes (IP) for the PatientAddress field.
 - PatientBloodType_IP: List of intended purposes (IP) for the PatientBloodType field.
 - PatientSSN_IP: List of intended purposes (IP) for the PatientSSN field.
 - PatientInsuranceProvider_IP: List of intended purposes (IP) for the PatientInsuranceProvider field.
 - PatientInsuranceNumber_IP: List of intended purposes (IP) for the PatientInsuranceNumber field.
 - ConsultingPhysician_IP: List of intended purposes (IP) for the ConsultingPhysician field.
"""


DB_PATH = 'sqlite:///medical_database.db'

GRADIO_PURPOSES = [
    ("General-Purpose", "General-Purpose"),
    ("|--- Clinical-Care", "Clinical-Care"), 
    ("|--- Research", "Research"), 
    ("|------- Public-Research", "Public-Research"), 
    ("|----------- Military-Research", "Military-Research"), 
    ("|----------- Non-Military-Research", "Non-Military-Research"), 
    ("|------- Private-Research", "Private-Research"), 
    ("|--- Patient-Support-Service", "Patient-Support-Service"), 
    ("|------- Billing", "Billing"), 
    ("|------- Communication", "Communication"), 
    ("|--- Third-Party", "Third-Party"), 
    ("|------- Marketing", "Marketing"), 
    ("|------- Product-Development", "Product-Development")]


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
