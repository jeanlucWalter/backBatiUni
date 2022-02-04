from ..models import *
import mysql.connector as db
import os
from dotenv import load_dotenv

class CreateNewDataBase:
  listTable = {"UserProfile":UserProfile, "JobForCompany":JobForCompany, "LabelForCompany":LabelForCompany, "Disponibility":Disponibility,"DetailedPost":DetailedPost, "Files":Files, "Post":Post, "Company":Company, "Job":Job, "Role":Role, "Label":Label}
  dictLabels = {
    "Qualibat":["Cet organisme apporte des réponses précises aux maitres d’œuvre et aux clients sur la capacité professionnelle de l’entreprise en explorant trois domaines précis : la situation administrative, l’envergure financière et les compétences techniques. Il délivre plusieurs certifications.","https://www.qualibat.com/",True],
    "Qualif'elec":["Si vous relevez du génie électrique et énergétique, Qualifelec est la certification qu’il vous faut obtenir absolument. Elle couvre 8 domaines d’activités précis : installations électriques., chauffage, ventilation, climatisation., branchements et réseaux., bâtiment communicant., éclairage public, courant faible., maintenance d’installations électriques., antenne.",	"https://www.qualifelec.fr/", True],
    "Quali’eau":["Ce label est destiné aux plombiers chauffagistes. C’est depuis 2003 que la réglementation impose cette certification. En effet, les conditions sanitaires d’installation de l’eau potable doivent être respectées pour éviter la multiplication des microbes comme la légionellose. Aussi, Quali’eau délivre des certifications portant sur trois grands axes : Enjeux et contexte réglementaire, maîtrise des techniques de conception de réseaux, Maîtrise des techniques de maintenance.", "https://www.capeb-paysdelaloire.fr/fich/qualieau.htm#demarche", True],
    "Quali’Sol":["Label attribué pour la qualité de l’installation des systèmes à énergie renouvelable particulièrement dans le domaine du solaire. Les équipements concernés sont : les Chauffe-eau Solaires Individuels (CESI), les Systèmes Solaires Combinés (SSC)", "https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/", True],
    "Quali’PV":["Rassurez-vous, ceci n’est pas le sigle de la certification des contractuelles pour les autoriser à mettre des PV, mais bien le label destiné à la qualification des installations d’énergie renouvelable par les systèmes photovoltaïques.",	"https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/", True],
    "Quali’Forage":["Ce label est attribué au professionnel installant des forages géothermiques sur nappe.",	"https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/", True],
    "Quali’Bois":["La certification est attribuée aux professionnels habilités à installer des chauffages au bois dans les habitations.",	"https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/", True],
    "Quali'Pac":["pour l’installation de pompes à chaleur",	"https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/é", True],
    "ISO 9001":["Pour obtenir la norme ISO 9001, l’entreprise doit justifier de son système de management et organisationnel. Elle mesure la satisfaction finale des clients ce qui est un gage de reconnaissance important pour votre entreprise. Malheureusement, elle est très difficile à obtenir et demande bien souvent l’aide d’un consultant extérieur.", "https://www.iso.org/fr/iso-9001-quality-management.html", True],
    "QSE":["Qualité Sécurité Environnement. Basée sur la norme ISO 9001, la certification QSE vérifie les mêmes domaines que l’ISO, mais aussi le respect de l’environnement par l’entreprise, la sécurité et la santé sur le lieu de travail. Elle aussi nécessite le recours à un consultant pour l’obtenir.", "", False],
    "RGE":["certification RGE permet aux particuliers de bénéficier des aides de l’Etat. Il devient indispensable de faire appel à un professionnel ayant obtenu le label RGE qui est un gage des compétences et de l’aptitude de l’artisan.", "https://www.service-public.fr/professionnels-entreprises/vosdroits/F32251", False],
    "FEE Bat":["Le label FEE Bat aborde les économies d’énergie en termes techniques, environnementaux, en matière d’arguments de vente mais également en terme de qualité de travaux. Il s’agit surtout d’une opportunité pour les professionnels du secteur de devenir un interlocuteur privilégié en conseillant en amont les clients sur leurs projets, en prescrivant et en mettant en œuvre les techniques qui concourent à la performance énergétique des bâtiments.",	"https://www.feebat.org/actualites/",True],
    "Artisant d'art":["Leur attribution atteste à la fois la formation et l'expérience professionnelle qui caractérisent le savoir-faire du secteur des métiers. Les titres sont des atouts commerciaux pour le chef d’entreprise artisanale, vis à vis de ses clients et des consommateurs. La qualité d’artisan d’art est attribuée aux personnes qui exercent une activité répertoriée dans la classification des métiers d’art.\nLes conditions pour obtenir la qualité d’artisan d’art :\n- exercer un métier de la liste et avoir :\n- soit un diplôme CAP, BEP ou équivalent dans le métier exercé,\n- soit une immatriculation au répertoire des métiers depuis plus de 3 ans.\nLa loi définit une liste de 198 métiers et 83 spécialités liés à la création, à la restauration du patrimoine et à la tradition qui permettent de rentrer dans la catégorie d’artisan d’art. Dans ces métiers rares et à forte valeur ajoutée, le label « artisan d’art » apporte une véritable preuve de savoir-faire.","https://www.cma-lyonrhone.fr/actualites/qualite-et-titre-dartisan-dart-comment-lobtenir",True],
    "Maitre artisan et maitre artisan en métier d’art":["L’artisan et l’artisan d’art peuvent prétendre au titre de maitre artisan dans 3 cas :\nEn étant titulaire du brevet de maitrise dans le métier exercé, délivrable après 2 ans de pratique professionnelle\nEn étant titulaire d’un diplôme de formation supérieur ou égal au brevet de maitrise, après avoir exercé son activité pendant 2 ans et après validation par la commission régionale de qualification. Être immatriculé au répertoire des métiers depuis plus de 10 ans et justifier auprès de la commission régionale de qualification d’un savoir-faire mis au service de la promotion de l’artisanat (participation à des travaux de recherche, à des évènements…) ou de la participation à des actions de formation (jury d’examen, formation d’apprentis…)","", True],
    "Meilleur ouvrier de France":["Ce titre prestigieux, qui conduit aussi à l’attribution d’un diplôme d’état, est obtenu à la suite de l’exigeant concours « Un des meilleurs ouvriers de France » organisé par le ministère de l’Éducation nationale tous les 3 à 4 ans.\nSavoir-faire, connaissances techniques modernes et traditionnelles, mais aussi créativité et dextérité sont évalués dans plus de 200 métiers différents.\nBien que la préparation de ce concours soit particulièrement exigeant, votre réussite sera gage de qualité exceptionnelle largement reconnu par les professionnels et par le grand public. Ce label renforce votre notoriété, en même temps qu’il promeut votre expertise dans votre domaine. Ne négligez pas ces précieux atouts pour la visibilité de votre entreprise et de vos produits","https://www.meilleursouvriersdefrance.info/accueil.html", True],
    "Maitres d’art":["Le dispositif Maitres d’art a été créé en 1994 pour valoriser les artisans engagés dans la transmission et la pérennisation de savoir-faire rares des métiers dans lesquels il n’existe plus de formation. Leur activité doit aussi participer à la vie économique et culturelle française. Véritable symbole d’un engagement et d’une volonté de transmission, cette certification donne aussi droit à une allocation annuelle de 16 000 euros pour la formation d’un apprenti.","https://www.maitredart.fr/",True],
    "Entreprise du Patrimoine Vivant":["Le label Entreprise du Patrimoine Vivant a été mis en place par l’Etat pour valoriser les entreprises françaises d’excellence. Pour y prétendre, une entreprise doit disposer d’un savoir-faire manufacturier traditionnel ou à haute technicité et être fortement attachée à un territoire. Outre le rayonnement en France et à l’étranger de ce label, il vous permet d’accéder à des crédits d’impôt et des aides au développement économique et à la visibilité.","https://www.institut-metiersdart.org/epv",True],
    "Handibat":["Les marques Handibat® / Silverbat® sont attribuées pour une période de trois ans et chaque année, une mise à jour est prévue afin qu’HB DEVELOPPEMENT, gestionnaire des marques Handibat®, Silverbat®, s’assure que les prérequis essentiels sont toujours satisfaits par votre entreprise : assurances professionnelles et cotisation annuelle à jour.","https://www.handibat.info/renouvellement-2020-pensez-y-des-maintenant/",False],
    "Chauffage+":["est une qualification complémentaire qui couvre la mise en place de chaudières à condensation ou micro-cogénération. Elle permet aux entreprises d’être qualifiée “RGE” pour l’installation d’équipements à haute performance énergétique dans le cadre de travaux de rénovation complémentaires aux énergies renouvelables.","https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/",False],
    "Ventilation+":["", "https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/", False],
    "Recharge Elec+":["", "https://www.qualit-enr.org/decouvrir-nos-qualifications-rge/", False],
    "Maison de qualité":["Créée en 1993 et concentrée à l’origine en Bretagne, l’association Maisons de qualité a pour mission première l’agrément des constructeurs de maisons individuelles.  Aujourd’hui présente sur le territoire national, elle a élaboré une charte qualité avec ses collaborateurs qui sont les associations de consommateurs, les organismes tels que l’ADIL et l’ADEME, les constructeurs de maisons et les partenaires industriels et institutionnels (GRDF, Orange, Engie, Crédit Mutuel…).\nChoisir un constructeur agréé « Maisons de qualité » c’est alors profiter d’un constructeur sélectionné pour son sérieux et son savoir-faire. L’association vous accompagne aussi dans vos démarches et s’assure de votre satisfaction.\nLe label ou marque « Maisons de qualité » n’est pas certifié comme les labels d’Etat et certains labels privés. Il est délivré par l’association elle-même de manière impartiale et profite malgré tout d’une reconnaissance technique objective.\nChoisir un constructeur agréé « Maisons de qualité » c’est alors profiter d’un constructeur sélectionné pour son sérieux et son savoir-faire. L’association vous accompagne aussi dans vos démarches et s’assure de votre satisfaction.\nLe label ou marque « Maisons de qualité » n’est pas certifié comme les labels d’Etat et certains labels privés. Il est délivré par l’association elle-même de manière impartiale et profite malgré tout d’une reconnaissance technique objective.","", True],
    "Maison de confiance FFCMI":["Née de la Fédération Française des Constructeurs de Maisons Individuelles, la FFC, cette marque témoigne des engagements du constructeur et des services proposés aux clients maîtres d’ouvrage. La FFC se veut être le seul syndicat professionnel indépendant dédié aux constructeurs. Ses missions sont la promotion de la profession et la protection du consommateur via notamment le Contrat de Construction de Maison Individuelle (CCMI). Dans ce sens, la FFC a créé la charte « Maison de confiance » pour identifier les constructeurs adhérents dans une démarche de valorisation de leurs prestations. Comme l’agrément « Maisons de qualité », « Maison de confiance » est une marque à ne pas interpréter comme un label certifié.","https://www.ffcmi.com/syndicat-constructeur-maison", False],
    "ECO Artisan":["", "", True],
    "PG (Professionnel du Gaz)":["", "", True],
    "Quali’ENR":["", "", True],		
    "QualiGaz":["", "", True],
  }
  listJobs = {"TCE (Tout Corps d'Etat)",
    "Autre: .....",
    "Acousticien	Acousticienne",
    "Agenceur de cuisines et de salles de bains",
    "Agent d'exploitation de l'eau	Agente d'exploitation de l'eau",
    "Agent hydrothermal	Agente hydrothermale",
    "Aide-conducteur de travaux",
    "Alarme Chantier",
    "Amiante",
    "Architecte",
    "Architecte d'intérieur",
    "Architecte naval	Architecte navale",
    "Ascensoriste",
    "Assistant en architecture Assistante en architecture",
    "Assistant d’entrepreneur du BTP",
    "Bainiste",
    "BIM manager",
    "Bronzier	Bronzière",
    "Bureau de contrôle",
    "Cabane Chantier et WC",
    "Câbleur",
    "Calculateur projeteur en béton armé",
    "Canalisateur	Canalisatrice",
    "Carreleur",
    "Carreleur faïenceur",
    "Carrossier	Carrossière",
    "Carrossier constructeur	Carrossière constructrice",
    "Carrossier reconstructeur	Carrossière reconstructrice",
    "Carrossier réparateur	Carrossière réparatrice",
    "Céramiste",
    "Chargé d'affaires en génie climatique	Chargée d'affaires en génie climatique",
    "Charpentier",
    "Chauffagiste",
    "Chef d'exploitation d'usine d'incinération	Cheffe d'exploitation d'usine d'incinération",
    "Chef d’équipe BTP	Cheffe d’équipe BTP",
    "Chef de chantier	Cheffe de chantier",
    "Coffreur-boiseur	Coffreuse-boiseuse",
    "Collaborateur d’architecte	Collaboratrice d’architecte",
    "Conducteur d'engins de travaux publics	Conductrice d'engins de travaux publics",
    "Conducteur d’engins	Conductrice d’engins",
    "Conducteur de travaux bâtiment	Conductrice de travaux bâtiment",
    "Conducteur opérateur	Conductrice opératrice de scierie",
    "Constructeur	Constructrice de routes",
    "Coordinateur de travaux	Coordinatrice de travaux",
    "Cordiste",
    "Couvreur	Couvreuse",
    "Couvreur-zingueur",
    "Cuisiniste	",
    "Débarras Cave",	
    "Degorgement/ Inspection Caméra",
    "Déménageur	Déménageuse",
    "Dépanneur	Dépanneuse en électroménager",
    "Désenfumage",
    "Designer",
    "Dessinateur technique	Dessinatrice technique",
    "Dessinateur-Projeteur	Dessinatrice-Projeteur",
    "Diagnostiqueur	Diagnostiqueuse immobilier",
    "Document administratif",
    "Domoticien	Domoticienne",
    "Ebéniste",
    "Echafaudage",
    "Econome de flux",
    "Economiste de la construction",
    "Elagueur	Elagueuse",
    "Electricien	Electricienne",
    "Electricien installateur	Electricienne installatrice",
    "Electromécanicien	Electromécanicienne",
    "Electronicien	Electronicienne automobile",
    "Electrotechnicien	Electrotechnicienne",
    "Employé	Employée d'élevage",
    "Etalagiste",
    "Etanchéiste",
    "Expert	Experte bilan carbone",
    "Façadier	Façadière",
    "Ferronnier	Ferronnière d'art",
    "Géomètre topographe",
    "Géotechnicien	Géotechnicienne",
    "Géothermicien	Géothermicienne",
    "Gestionnaire",
    "Grutier Grutière",
    "Ingénieur chimiste	Ingénieure chimiste",
    "Ingénieur d’affaires du BTP	Ingénieure d’affaires du BTP",
    "Ingénieur électricien	Ingénieure électricienne",
    "Ingénieur en Aménagement et Urbanisme	Ingénieure en Aménagement et Urbanisme",
    "Ingénieur en chef territorial	Ingénieure en chef territoriale",
    "Ingénieur en Génie Civil	Ingénieure en Génie Civil",
    "Ingénieur études de prix	Ingénieure études de prix",
    "Ingénieur structure	Ingénieure structure",
    "Isolation Thermique",
    "Logiciel comptable",
    "logiciel devis/facture Bat…",
    "Logiciel gestion planning",
    "Machiniste-constructeur ou plateau	Machiniste-constructrice ou plateau",
    "Maçon	Maçonne",
    "Maître d’œuvre	Maîtresse d’œuvre",
    "mécanicien	mécanicienne bateaux",
    "mécanicien de fabrication",
    "mécanicien de maintenance des matériels",
    "mécanicien de maintenance industrielle",
    "mécanicien de précision",
    "mécanicien-outilleur	mécanicienne-outilleuse",
    "mécanicien-réparateur	mécanicienne-réparatrice en matériel agricole",
    "menuisier",
    "Métreur",
    "Miroitier",
    "Modéliste",
    "Monteur	Monteuse en installations thermiques et climatiques",
    "Monteur-câbleur	Monteuse-câbleuse",
    "Nettoyage comble",
    "Opérateur	Opératrice en traitement des matériaux",
    "Orga Chantier affichage",
    "Ouvrier	Ouvrière agricole",
    "Paysagiste",
    "Peintre",
    "Peintre décorateur",
    "Peintre en bâtiment",
    "Plaquiste",
    "Plâtrier",
    "Plombier",
    "Programmiste",
    "Rédacteur territorial	Rédactrice territoriale",
    "Régleur	Régleuse",
    "Responsable de site de traitement des déchets",
    "Restaurateur d’art",
    "Sculpteur	Sculptrice sur bois",
    "Secrétaire",
    "Secrétaire administratif	Secrétaire administrative",
    "Serrurier	Serrurière",
    "Serrurier dépanneur	Serrurière dépanneuse",
    "Serrurier-métallier	Serrurière-métallière",
    "Solier-moquettiste",
    "Soudeur	Soudeuse",
    "Souscripteur	Souscriptrice",
    "Staffeur-ornemaniste	Staffeuse-ornemaniste",
    "Tableau Électrique Chantier ( M?)",
    "Tailleur de pierre	Tailleuse de pierre",
    "Tapissier d'ameublement	Tapissière d'ameublement",
    "Technicien automobile	Technicienne automobile",
    "Technicien de la construction	Technicienne de la construction",
    "Technicien électrotechnicien	Technicienne électrotechnicienne",
    "Technicien Expert VRD	Technicienne Expert VRD",
    "Technicien forestier	Technicienne forestière",
    "Technicien thermicien	Technicienne thermicienne",
    "Terrassier",
    "Verrier au chalumeau	Verrière au chalumeau",
    "Vitrailliste",
    "Vitrier	Vitrière",
  }	

  def __init__(self):
    load_dotenv()
    self.connection = db.connect(
      user = os.getenv('DB_USERNAME'),
      password = os.getenv('DB_PASSWORD'),
      host = os.getenv('DB_HOST'),
      database = os.getenv('DB_NAME'),
    )
    self.cursor = self.connection.cursor()

  def reloadDataBase(self):
    print("reloadDataBase")
    answer = self.emptyDataBase()
    return self.fillupDataBase(answer)

  def emptyDataBase (self):
    for dir in ['./files/admin/', './files/avatars/', './files/labels/', './files/posts/']:
      for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
    for table in CreateNewDataBase.listTable.values():
      table.objects.all().delete()
      tableName = table.objects.model._meta.db_table
      self.cursor.execute(f"ALTER TABLE {tableName} AUTO_INCREMENT=1;")
    for user in User.objects.all():
      if user.username != "jlw":
        user.delete()
    self.cursor.execute("ALTER TABLE auth_user AUTO_INCREMENT=1;")
    return {"emptyDataBase":"OK"}

  def fillupDataBase (self, response= {}):
    for function in reversed(CreateNewDataBase.listTable):
      table = CreateNewDataBase.listTable[function]
      for key, value in getattr(self, "fillup" + function)(table).items():
        response[key] = value
    self.connection.close() 
    return response

  def fillupUserProfile(self, table):
    UserProfile.objects.create(userNameInternal=User.objects.get(username="jlw"), Company=Company.objects.get(name="BatiUni"), firstName="Eric", lastName="Walter", cellPhone="06 34 09 06 95", token=None)
    return {"create user profile":"OK"}

  def fillupCompany(self, table):
    Company.objects.create(name="BatiUni", siret="123456789", capital=123456, revenue=654321.22, webSite="https://stackoverflow.com")
    return {}
  def fillupLabelForCompany(self, table): return {} 
  def fillupJobForCompany(self, table):return {}
  def fillupFiles(self, table):return {}
  def fillupPost(self, table): return {}
  def fillupDetailedPost(self, table): return {}
  def fillupDisponibility(self, table): return {}

  def fillupJob(self, table):
    for job in self.listJobs:
      table.objects.create(name=job)
    return {"fillupJob":"OK"}

  def fillupRole(self, table):
    listRole = ["Une entreprise à la recherche de sous-traitances", "Un sous-traitant à la recherche d'une entreprise", "Les deux"]
    for role in listRole:
      table.objects.create(name=role)
    return {"fillupRole":"OK"}

  def fillupLabel(self, table):
    # listLabel = ['Qualibat', 'RGE', 'RGE Eco Artisan', 'NF', 'Effinergie', 'Handibat', 'Qualifelec', 'Qualit’EnR', 'Quali’Sol', 'Quali’Bois', 'Quali’PV', 'Quali’Pac', 'Certibat', 'CERQUAL Qualitel Certification', 'Autres...']
    for label in self.dictLabels.keys():
      table.objects.create(name=label)
    return {"fillupLabel":"OK"}




