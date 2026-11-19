"""Single source of truth for SATs products, shared by build.py and optimise_images.py."""

SITE = {
    "domain": "https://satsolutions.in",
    "brand": "SATs",
    "long_name": "Semiconductor Analysis and Testing Solutions",
    "phone_display": "(+91) 7990042066",
    "phone_tel": "+917990042066",
    "wa_number": "917990042066",          # country code 91 + number
    "email": "info.sats123@gmail.com",
    "address_lines": ["IIC, PDPU Hostel Road, Raysan", "Gandhinagar 382007,", "Gujarat (GJ),", "India."],
    "address_one_line": "IIC, PDPU Hostel Road, Raysan, Gandhinagar 382007, Gujarat, India",
    "hours": "Mon–Sat: 10 AM – 6 PM",
    "brochure": "https://drive.google.com/file/d/1riaZfss7LC43V-YRTEBJp3RS1cmoGfui/view?usp=sharing",
    "hero_video": "https://www.youtube.com/watch?v=sHt4WsGVrug",
    "contact_form": "https://docs.google.com/forms/d/e/1FAIpQLSdh9vxo56nTxRRt2CsZc91lJZirI084tV9nfFe1WmMvhtUIvQ/viewform?usp=sf_link",
    "social": [
        ("facebook", "Facebook", "https://www.facebook.com/profile.php?id=61559400863942"),
        ("linkedin", "LinkedIn", "https://www.linkedin.com/in/semiconductor-analysis-and-testing-solutions-sats-8a4a29307/"),
        ("youtube", "YouTube", "https://www.youtube.com/@Semiconductortestingsolutions"),
    ],
    "credit_url": "https://iamshreeji-copy1.github.io/ravindrakumar_purohit/index.html",
    "gtag": "G-TMP95ECSDY",
    "gtm": "GTM-TQ2FD6NJ",
}

CAT_LABEL = {"equipment": "Equipment", "consult": "Consultation", "edu": "Education"}

P = "assets/img/sats_products/"
PROBE = P + "probe_station/"

# key: slug used for images; file: existing page URL (kept so no existing link breaks)
PRODUCTS = [
    dict(key="low-temp-probe-station", file="portfolio-details-low-temp-probe-station.html",
         name="Low-Temperature Micro-Probe Station", card_title="Low-Temperature Micro-Probe Station",
         cat="equipment", icon="bi-cpu", fit="cover",
         imgs=[PROBE + "SATs Probe Station.jpg", PROBE + "IMG_20240510_163524.jpg",
               PROBE + "Minimalist Black and White Blank Paper Document (1).jpg"],
         short="High-precision micro probe station for detailed semiconductor testing and analysis, from -40 °C to 120 °C under vacuum."),
    dict(key="micro-probe-station-alt", file="portfolio-details-Probesstation.html",
         name="Low-Temperature Micro-Probe Station", card_title=None, cat="equipment", icon="bi-cpu", fit="cover",
         imgs=[PROBE + "SATs Probe Station.jpg", PROBE + "IMG_20240510_163524.jpg",
               PROBE + "Minimalist Black and White Blank Paper Document (1).jpg"],
         short="High-precision micro probe station for detailed semiconductor testing and analysis, from -40 °C to 120 °C under vacuum.",
         canonical_of="portfolio-details-low-temp-probe-station.html", in_grid=False),
    dict(key="sample-holder", file="portfolio-details-sample-holder-final.html", name="Sample Holder", card_title="Sample Holder",
         cat="equipment", icon="bi-grid-3x3-gap", fit="contain",
         imgs=[P + "sample_holder/Sample-Holder1.jpg", P + "sample_holder/Sample-Holder2.jpg", P + "sample_holder/Sample-Holder3.jpg"],
         short="Sample holder for thin films and solar cells with spring-contact protection and pixel switching."),
    dict(key="pec-setup", file="portfolio-details-pec-setup.html", name="PEC Setup", card_title="PEC Setup",
         cat="equipment", icon="bi-brightness-high", fit="contain", imgs=[P + "pec_setup/PEC-Setup1.jpg"],
         short="Photoelectrochemical setup for studying how light interacts with semiconductor materials."),
    dict(key="light-source", file="portfolio-details-light-source.html", name="Light Source", card_title="Light Source (1 Sun)",
         cat="equipment", icon="bi-lightning-charge", fit="contain",
         imgs=[P + "light_source/Light-sorce1.jpg", P + "light_source/Light-sorce2.jpg"],
         short="1000 W/m² (1 Sun) programmable light source for precise, repeatable illumination."),
    dict(key="hydrothermal-autoclave", file="portfolio-details-hydro-thermal-autoclave.html", name="Hydrothermal Autoclaves",
         card_title="Hydrothermal Autoclave", cat="equipment", icon="bi-box-seam", fit="cover",
         imgs=[P + "hydro_thermal/Hydrothermal1.jpg", P + "hydro_thermal/Hydrothermal2.jpg"],
         short="Nonmagnetic 316 stainless-steel autoclaves with PTFE inner vessels in volumes from 25 mL upwards."),
    dict(key="battery-tester", file="portfolio-details-sample-battery-tester.html", name="Battery Tester", card_title="Battery Tester",
         cat="equipment", icon="bi-battery-charging", fit="cover",
         imgs=[P + "bettery_tester/Bettery-tester1.jpg", P + "bettery_tester/Bettery-tester2.jpg"],
         short="Battery testing instrument from SATs. Contact us for specifications and configurations.",
         spec_on_request=True),
    dict(key="water-chiller", file="portfolio-details-Water-chiller-solutions.html", name="Water Chiller Solutions", card_title="Water Chiller",
         cat="equipment", icon="bi-droplet", fit="contain", imgs=[P + "chiller/Chiller1.png"],
         short="Heavy-duty water chiller for rapid, efficient cooling of lab and industrial equipment."),
    dict(key="externally-controlled-cryo-probe-station", file="portfolio-details-Externally-Probe-Controlled-Cryogenic-Probe-Station.html",
         name="Externally Probe-Controlled Cryogenic Probe Station", card_title="Externally Probe-Controlled Cryogenic Probe Station",
         cat="equipment", icon="bi-thermometer-snow", fit="contain",
         imgs=[P + "extranal_prob_crayo_1.png", P + "extranal_prob_crayo_2.jpg"],
         short="Temperature-dependent electrical and material characterisation from cryogenic to high temperature, without vacuum breaks."),
    dict(key="cryogenic-probe-station", file="portfolio-details-cryogenic-probe-station.html", name="Cryogenic Probe Station",
         card_title="Cryogenic Probe Station", cat="equipment", icon="bi-snow2", fit="cover",
         imgs=[P + "crayo_1.jpg", P + "crayo_2.jpeg", P + "crayo_3.png"],
         short="Cryogenic probe station for electrical characterisation from -196 °C to +300 °C (upgradable to +550 °C)."),
    dict(key="potentiostat", file="portfolio-details-SATS Potentiostat.html", name="SATS Potentiostat", card_title="SATS Potentiostat",
         cat="equipment", icon="bi-graph-up-arrow", fit="contain", imgs=[P + "SATs Potentiostate.png"],
         short="Compact potentiostat/galvanostat (MedPstat 2.0 Advance) for CV, LSV and other electrochemical measurements."),
    dict(key="muffle-furnace", file="portfolio-details-Muffle-Furnace.html", name="Muffle Furnace", card_title="Muffle Furnace",
         cat="equipment", icon="bi-fire", fit="contain", imgs=[P + "Furnace_1.png"],
         short="High-temperature furnace for material synthesis, sintering and heat treatment with PID control."),
    dict(key="vibration-less-table", file="portfolio-details-vibrationless-table.html", name="Vibration-less Table",
         card_title="Vibration-less Table", cat="equipment", icon="bi-arrows-collapse", fit="contain", imgs=[P + "VbTable.png"],
         short="Honeycomb-core table with air-spring isolation legs, built to eliminate vibrations from your experiments."),
    dict(key="lab-equipment-custom-solutions", file="portfolio-details-custom-solutions-and-lab-equipments.html",
         name="Lab Equipment & Custom Solutions", card_title="Lab Equipment & Custom Solutions", cat="consult", icon="bi-tools", fit="cover",
         imgs=[P + "custom_solutions_and_lab_equiment_supplier/Custom-solution1.jpg", P + "custom_solutions_and_lab_equiment_supplier/Custom-solution2.jpg",
               P + "custom_solutions_and_lab_equiment_supplier/Custom-solution3.jpg", P + "custom_solutions_and_lab_equiment_supplier/Custom-solution4.jpg"],
         card_index=1, short="Supply and customisation of laboratory instruments, with installation, training and support."),
    dict(key="web-design-development", file="portfolio-details-web-design-and-development-done.html", name="Web Design & Development",
         card_title="Web Design & Development", cat="consult", icon="bi-globe2", fit="cover",
         imgs=[P + "web_design_and_development/Web-design1.jpg", P + "web_design_and_development/Web-design2.jpg",
               P + "web_design_and_development/Web-design3.jpg"],
         short="Responsive, user-friendly websites tailored to your needs."),
    dict(key="ai-ml-course", file="portfolio-details-ai-ml-course.html", name="AI/ML Courses", card_title="AI/ML Courses",
         cat="edu", icon="bi-mortarboard", fit="cover",
         imgs=[P + "ai_ml_course/AIML1.jpg", P + "ai_ml_course/AIML2.jpg", P + "ai_ml_course/AIML3.jpg"],
         short="End-to-end AI/ML course for researchers in semiconductors and materials science."),
    dict(key="automation", file="portfolio-details-automation.html", name="End-to-End Automation", card_title=None,
         cat="consult", icon="bi-robot", fit="cover", imgs=[], in_grid=False, custom_content="automation",
         short="Automated sample handling, data acquisition, analysis and reporting, tailored to your lab."),
]

# Pages that are not products
ARCHIVE = [
    "updated_index.html", "updated indexx_1.html", "index__UNDER_MAINTENCANCE.html", "sample-inner-page.html",
    "blog.html", "blog-details.html", "portfolio-details.html",
]

# Product spec items that were copy-pasted from the Micro-Probe Station page onto other products' pages.
# (term, page-keys on which they are wrong). Matching also requires the body text to be identical to the probe page.
PROBE_COPY_TERMS = {
    "Temperature Versatility", "Vacuum Compatibility", "Optical Characterization Capability", "Electrode Configuration",
    "XYZ Positioning Control", "Compatibility with Electrical Measurement Devices:", "Widely used in the semiconductor R&D",
}
PROBE_PAGE_KEYS = {"low-temp-probe-station", "micro-probe-station-alt"}

# Headings that the legacy markup split across tags
TEXT_FIXUPS = {
    ("ai-ml-course", "Optimization"): ("Optimization Process", "Process "),
    ("ai-ml-course", "Data Analysis"): ("Big Data Analysis", "Big "),
}

SERVICES = [
    # (title, text, icon, product key or None -> contact)
    ("Micro Probe Stations", "Our high-precision micro probe stations are ideal for detailed semiconductor testing and analysis. These stations provide accuracy and reliability, essential for advanced research.", "bi-cpu", "low-temp-probe-station"),
    ("Sample Holders", "We offer a variety of sample holders that are designed to securely hold different types of semiconductor samples, ensuring stability and precision during testing procedures.", "bi-grid-3x3-gap", "sample-holder"),
    ("Autoclaves", "Our autoclaves are equipped with advanced features to provide efficient and effective sterilization for your semiconductor equipment and samples.", "bi-box-seam", "hydrothermal-autoclave"),
    ("PEC Setups", "We provide Photoelectrochemical (PEC) setups that are essential for studying the interactions between light and semiconductor materials, facilitating cutting-edge research in solar energy and other applications.", "bi-brightness-high", "pec-setup"),
    ("Externally Probe-Controlled Cryogenic Probe Station", "High-precision platform enabling temperature-dependent electrical and material characterization from cryogenic to high-temperature environments without vacuum breaks. Ideal for semiconductor and MEMS device evaluation.", "bi-thermometer-snow", "externally-controlled-cryo-probe-station"),
    ("SATS Potentiostat", "Compact potentiostat/galvanostat for accurate electrochemical measurements including CV, LSV, and corrosion analysis. Perfect for battery, supercapacitor, and sensor research.", "bi-graph-up-arrow", "potentiostat"),
    ("Muffle Furnace", "High-temperature furnace for material synthesis, heat treatment, and metallurgical studies with advanced PID temperature control and robust safety systems.", "bi-fire", "muffle-furnace"),
    ("Cryogenic Probe Station", "Engineered for advanced semiconductor research, this station delivers high accuracy and stable performance for precise electrical characterization under a wide range of controlled temperatures.", "bi-snow2", "cryogenic-probe-station"),
    ("Vibration-less Table", "Experience ultimate stability with a table designed to eliminate vibrations from your experiments, ensuring precision for optical, semiconductor, and material science research.", "bi-arrows-collapse", "vibration-less-table"),
    ("AI-ML in E2E Solution", "Harness the power of Artificial Intelligence and Machine Learning with our predictive analysis services. We help you forecast trends and outcomes, enabling smarter decision-making in semiconductor research and development, also, end-to-end automation solutions streamline your research and testing processes, enhancing efficiency and accuracy. We tailor our automation systems to fit your specific needs, ensuring seamless integration and operation.", "bi-robot", "automation"),
    ("Lab Instrument Supply", "As a leading supplier of laboratory instruments, we offer a wide range of high-quality equipment necessary for semiconductor testing and analysis.", "bi-tools", "lab-equipment-custom-solutions"),
    ("Website Development", "We offer website development services tailored to your needs, specializing in creating responsive, user-friendly sites for various purposes such as personal blogs, e-commerce, and more. Partner with us to bring your digital vision to life.", "bi-globe2", "web-design-development"),
    ("Industry Consultation", "We offer industry consultation services tailored for sectors like the semiconductor and EdTech industries. Our expertise provides strategic guidance and innovative solutions to help businesses thrive. Partner with us to advance your industry goals.", "bi-briefcase", None),
    ("Semiconductor Fabrication Services", "We specialize in industry services for semiconductor manufacturing setup, offering strategic guidance and innovative solutions to optimize operations. Partner with us to enhance your semiconductor manufacturing capabilities.", "bi-buildings", None),
]

CLIENTS = [
    ("iitd.png", "IIT Delhi"), ("University_of_Hyderabad_Logo.png", "University of Hyderabad"), ("IISER-K_Logo.png", "IISER Kolkata"),
    ("iitk.png", "IIT Kanpur"), ("iitgn.png", "IIT Gandhinagar"), ("iitmandi.png", "IIT Mandi"), ("iit_dhanbad.png", "IIT (ISM) Dhanbad"),
    ("iiser_tirupati.png", "IISER Tirupati"), ("CUG.png", "Central University of Gujarat"), ("cuh_hariyana.png", "Central University of Haryana"),
    ("purvanchal_university.png", "Purvanchal University"), ("shiv_nadar.jpg", "Shiv Nadar University"), ("manipal.jpeg", "Manipal University"),
    ("nitte.png", "NITTE University"), ("PDEU.png", "Pandit Deendayal Energy University"), ("csir_hyderabad.png", "CSIR Hyderabad"),
    ("adani_solar.jpg", "Adani Solar"), ("dhruva_space.png", "Dhruva Space"), ("bits_goaa.jpg", "BITS Goa"),
    ("bits_hyderabad.png", "BITS Hyderabad"), ("au_logo.png", "AU"),
]

TESTIMONIALS = [
    ("charu-dubey_800_800.png", "Charu Dubey", "Research Scholar",
     "Learning semiconductor analysis and testing here was transformative. Expert instructors and top-notch solutions provided invaluable hands-on experience. Highly recommended!"),
    ("om_modi.png", "Om Modi", "Freelancer",
     "Working with ML models for semiconductor analysis and prediction here was outstanding. The instructors were experts, and the hands-on experience with cutting-edge solutions was invaluable. Thanks SATs ❤️"),
    ("paawnkumar.jpg", "Pawn Kumar", "Researcher",
     "Exploring material synthesis and characterization methods offered hands-on experience with cutting-edge techniques for practical expertise. Highly valuable this innovative learning journey!"),
]


# ---------------------------------------------------------------- Phase 2: at-a-glance + explorers
# Every figure below is copied from the product's own specification text (nothing invented).
# (prefix, number, suffix, label, decimals)   number=None -> plain text value (prefix)
_CRYO = [("", -196, " to +300 °C", "Temperature range", 0), ("", 50, " °C/min", "Max heating rate", 0),
         ("", 20, " °C/min", "Max cooling rate", 0), ("±", 0.1, " °C", "Stability & resolution", 1)]
GLANCE = {
    "low-temp-probe-station": [("", -40, " to 120 °C", "Stage range (no liquid nitrogen)", 0), ("", 350, " °C", "High-temp option (from ambient)", 0),
                               ("", 4, " electrodes", "Pure tungsten, 50 µm tips", 0), ("5×10⁻² ", None, "Torr", "Vacuum capability", 0)],
    "cryogenic-probe-station": _CRYO,
    "externally-controlled-cryo-probe-station": _CRYO,
    "muffle-furnace": [("Up to ", 1500, " °C", "Model range from ambient", 0), ("±", 1, " °C", "Temperature accuracy", 0),
                       ("", 30, " °C/min", "Max heating rate", 0), ("1–", 20, " L", "Chamber volume", 0)],
    "potentiostat": [("±", 10, " V", "Applied potential range", 0), ("±", 250, " mA", "Maximum current", 0),
                     ("", 7, " ranges", "Current ranges, 10 nA – 250 mA", 0), ("", 10, " TΩ", "Input impedance", 0)],
    "hydrothermal-autoclave": [("", 316, " SS", "Nonmagnetic stainless-steel shell", 0), ("PTFE / PPL", None, "", "Research-grade inner vessel", 0),
                               ("25–", 2500, " mL", "Volume options", 0), ("", 9, " sizes", "Available volumes", 0)],
    "light-source": [("", 1000, " W/m²", "Output (1 Sun)", 0), ("", 6500, " K", "Colour temperature", 0),
                     ("Programmable", None, "", "Adjustable intensity", 0), ("Pulsing", None, "", "Optional provision", 0)],
    "water-chiller": [("", 400, " W", "Rapid cooling capacity", 0), ("", -5, " to 55 °C", "Operating range", 0),
                      ("", 5, " L", "Water tank", 0), ("", 5, " L/min", "Circulation pump flow", 0)],
}
GLANCE["micro-probe-station-alt"] = GLANCE["low-temp-probe-station"]

# Interactive "range explorer": (title, min, max, unit, default, heat °C/min, cool °C/min, note, [(value,label)...], [(from,to,label)...])
RANGE = {
    "cryogenic-probe-station": dict(title="Temperature range explorer", min=-196, max=550, std_max=300, default=25, heat=50, cool=20,
        note="Standard range −196 °C to +300 °C; upgrades to +400 °C or +550 °C are optional.",
        marks=[(-196, "−196"), (25, "25"), (300, "+300"), (550, "+550")],
        zones=[(300, "Within the standard range"), (400, "Needs the optional +400 °C upgrade"), (550, "Needs the optional +550 °C upgrade")]),
    "externally-controlled-cryo-probe-station": dict(title="Temperature range explorer", min=-196, max=550, std_max=300, default=25, heat=50, cool=20,
        note="Standard range −196 °C to +300 °C; optional upgrades go up to +550 °C.",
        marks=[(-196, "−196"), (25, "25"), (300, "+300"), (550, "+550")],
        zones=[(300, "Within the standard range"), (550, "Needs an optional upgrade (up to +550 °C)")]),
    "muffle-furnace": dict(title="Model range explorer", min=25, max=1500, std_max=1500, default=800, heat=30, cool=None,
        note="Models: 800 / 1000 / 1200 / 1400 / 1500 °C, from ambient.",
        marks=[(25, "25"), (800, "800"), (1000, "1000"), (1200, "1200"), (1400, "1400"), (1500, "1500")],
        zones=[(800, "Reached by every model (800 °C and up)"), (1000, "Needs the 1000 °C model or higher"), (1200, "Needs the 1200 °C model or higher"),
               (1400, "Needs the 1400 °C model or higher"), (1500, "Needs the 1500 °C model")]),
    "low-temp-probe-station": dict(title="Stage temperature explorer", min=-40, max=350, std_max=120, default=25, heat=None, cool=None,
        note="Stage: −40 °C to 120 °C without liquid nitrogen, or ambient to 350 °C for high-temperature applications.",
        marks=[(-40, "−40"), (25, "25"), (120, "120"), (350, "350")],
        zones=[(120, "Within the stage range – no liquid nitrogen needed"), (350, "High-temperature configuration (ambient to 350 °C)")]),
}
RANGE["micro-probe-station-alt"] = RANGE["low-temp-probe-station"]
