import json
import re
import os

# Chemin du dossier contenant les fichiers JSON
json_folder = "/home/ubuntu/ETL/Json_scraping"
# Chemin du dossier de sortie
output_folder = "/home/ubuntu/ETL/Json_transformed"

# Créer le dossier de sortie s'il n'existe pas
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Revoir les intitulés de postes
JOBS = {
    "data engineer": (("data", "engineer"), ("data", "ingénieur")),
    "data architect": (("data", "architect"), ("architect", "si"), ("architect", "it")),
    "data scientist": (("data", "scientist"), ("science", "donnée")),
    "data analyst": (("data", "analyst"), ("data", "analytics")),
    "software engineer": (("software", "engineer"), ("software", "developer"), ("développeur", "logiciel"), ("ingénieur", "logiciel")),
    "devops": ("devops",),
    "data warehousing engineer": ("data", "warehouse", "engineer"),
    "machine learning engineer": (("machine", "learning", "engineer"), ("ml", "engineer")),
    "cloud architect /engineer ": (("cloud", "architect"), ("cloud", "engineer"), ("cloud", "ingénieur"), ("cloud", "engineer"), ("AWS",), ("GCP",), ("azure",)),
    "solution architect": ("solution", "architect"),
    "big data engineer": (("big", "data", "engineer"), ("ingénieur", "big", "data")),
    "big data developer": (("big", "data", "developer"), ("développeur", "big", "data")),
    "data infrastructure engineer": ("data", "infrastructure", "engineer"),
    "data pipeline engineer": ("data", "pipeline", "engineer"),
    "etl developer": ("etl",),
    "business developer": (("business", "developer"), ("sales", "developer")),
    "business analyst": ("business", "analyst"),
    "cybersecurity": (("cyber", "security"), ("cyber", "sécurité"), ("cyber", "risk"), ("cyber", "risque")),
    "sysops": ("sysops",),
    "consultant data": ("data", "consultant"),
}

def find_job_title(title, jobs_dict):
    title_lower = title.lower()

    for job, keywords in jobs_dict.items():
        if isinstance(keywords[0], tuple):
            for keyword_tuple in keywords:
                if all(word in title_lower for word in keyword_tuple):
                    return job
        else:
            if all(word in title_lower for word in keywords):
                return job

    return "Other"

# Liste de mots de référence
reference_words = [
    "AWS", "Adaptability", "Airflow", "Alibaba Cloud", "Ansible", "Apache Airflow", "Apache Flink", 
    "Apache Kafka", "Avro", "Azure", "Backend Development", "Bash", "Bayesian Statistics", 
    "Big Data", "Big Query", "BigQuery", "C#", "C++", "CI / CD", "CI/CD", "Cassandra", "CatBoost", 
    "Chef", "Cloud", "CloudFormation", "Collaboration", "Communication", "Confluence", "Creativity", 
    "Critical Thinking", "Databricks", "DevOps", "Discord", "Docker", "Elasticsearch", "Empathy", 
    "Firewall", "Flexibility", "Flink", "GCP", "Git", "Google Cloud Platform", "HBase", "Hadoop", 
    "Hyper-V", "IBM Cloud", "Inférentielles", "Initiative", "Interpersonal Skills", "JIRA", "Java", 
    "Jenkins", "Json", "Julia", "Keras", "Kotlin", "Kubernetes", "Leadership", "LightGBM", "Linux", 
    "MATLAB", "ML", "MacOS", "Machine Learning", "Matplotlib", "Microsoft Teams", "MongoDB", "MySQL", 
    "Neo4j", "NoSQL", "NumPy", "OpenShift", "Oracle SQL", "Orange", "Organization", "Pandas", 
    "Plotly", "PostgreSQL", "Power BI", "Problem Solving", "Protocol Buffers", "Puppet", "PyTorch", 
    "Python", "R", "SQL", "SQL Server", "SSL/TLS", "Scala", "Scikit-Learn", "Seaborn", "SingleStore", 
    "Slack", "Snowflake", "Spark", "Statistiques", "Statistiques Bayésiennes", "Statistiques Descriptives", 
    "Stress Management", "Tableau", "Teams", "Teamwork", "TensorFlow", "Terraform", "Time Management", 
    "Travis CI", "VMware", "VPN", "VirtualBox", "Windows", "Wireshark", "XGBoost", "XML",
]

# Convertir la liste de mots de référence en minuscules
reference_words_lower = [word.lower() for word in reference_words]

# Fonction pour nettoyer et remplacer une liste de mots
def nettoyer_et_remplacer_liste(liste):
    if liste is None:
        return None
    nettoye = []
    for mot in liste:
        mot_nettoye = re.sub(r"[^\w\s]", "", mot).strip().lower()
        if len(mot_nettoye) < 4:
            for ref_word, ref_word_lower in zip(reference_words, reference_words_lower):
                if re.fullmatch(ref_word_lower, mot_nettoye):
                    nettoye.append(ref_word)
                    break
            else:
                nettoye.append(mot_nettoye)
        else:
            for ref_word, ref_word_lower in zip(reference_words, reference_words_lower):
                if ref_word_lower in mot_nettoye:
                    nettoye.append(ref_word)
                    break
            else:
                nettoye.append(mot_nettoye)
    return list(set([mot for mot in nettoye if mot]))  # Supprimer les doublons


# Fonction pour nettoyer la liste d'expérience
def nettoyer_experience(liste):
    if liste is None:
        return None
    nettoye = [mot for mot in liste if mot not in {'a', 'n', 's'}]
    return list(set(nettoye))


# Parcourir chaque fichier JSON dans le dossier
for filename in os.listdir(json_folder):
    if filename.endswith(".json"):
        filepath = os.path.join(json_folder, filename)
        
        # Lire le fichier JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Appliquer les modifications
        for entry in data:
            title = entry.get('title', '')
            if title:
                entry['job_title'] = find_job_title(title.lower(), JOBS)
            else:
                entry['job_title'] = "Other"

            if "skills" in entry and entry["skills"] is not None:
                for skill_category, skill_list in entry["skills"].items():
                    entry["skills"][skill_category] = nettoyer_et_remplacer_liste(skill_list)

            if "details" in entry and entry["details"] is not None:
                if "Experience" in entry["details"] and entry["details"]["Experience"] is not None:
                    entry["details"]["Experience"] = nettoyer_experience(entry["details"]["Experience"])

        # Construire le chemin du fichier de sortie avec le suffixe _updated
        output_filepath = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_updated.json")

        # Sauvegarder le fichier JSON modifié
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

print("Les données mises à jour ont été sauvegardées.")
