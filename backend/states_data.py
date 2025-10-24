# Indian States and Union Territories Data

INDIAN_STATES = [
    {"code": "AN", "name": "Andaman and Nicobar Islands", "name_hi": "अंडमान और निकोबार द्वीप समूह"},
    {"code": "AP", "name": "Andhra Pradesh", "name_hi": "आंध्र प्रदेश"},
    {"code": "AR", "name": "Arunachal Pradesh", "name_hi": "अरुणाचल प्रदेश"},
    {"code": "AS", "name": "Assam", "name_hi": "असम"},
    {"code": "BR", "name": "Bihar", "name_hi": "बिहार"},
    {"code": "CH", "name": "Chandigarh", "name_hi": "चंडीगढ़"},
    {"code": "CT", "name": "Chhattisgarh", "name_hi": "छत्तीसगढ़"},
    {"code": "DN", "name": "Dadra and Nagar Haveli and Daman and Diu", "name_hi": "दादरा और नगर हवेली और दमन और दीव"},
    {"code": "DL", "name": "Delhi", "name_hi": "दिल्ली"},
    {"code": "GA", "name": "Goa", "name_hi": "गोवा"},
    {"code": "GJ", "name": "Gujarat", "name_hi": "गुजरात"},
    {"code": "HR", "name": "Haryana", "name_hi": "हरियाणा"},
    {"code": "HP", "name": "Himachal Pradesh", "name_hi": "हिमाचल प्रदेश"},
    {"code": "JK", "name": "Jammu and Kashmir", "name_hi": "जम्मू और कश्मीर"},
    {"code": "JH", "name": "Jharkhand", "name_hi": "झारखंड"},
    {"code": "KA", "name": "Karnataka", "name_hi": "कर्नाटक"},
    {"code": "KL", "name": "Kerala", "name_hi": "केरल"},
    {"code": "LA", "name": "Ladakh", "name_hi": "लद्दाख"},
    {"code": "LD", "name": "Lakshadweep", "name_hi": "लक्षद्वीप"},
    {"code": "MP", "name": "Madhya Pradesh", "name_hi": "मध्य प्रदेश"},
    {"code": "MH", "name": "Maharashtra", "name_hi": "महाराष्ट्र"},
    {"code": "MN", "name": "Manipur", "name_hi": "मणिपुर"},
    {"code": "ML", "name": "Meghalaya", "name_hi": "मेघालय"},
    {"code": "MZ", "name": "Mizoram", "name_hi": "मिजोरम"},
    {"code": "NL", "name": "Nagaland", "name_hi": "नागालैंड"},
    {"code": "OR", "name": "Odisha", "name_hi": "ओडिशा"},
    {"code": "PY", "name": "Puducherry", "name_hi": "पुडुचेरी"},
    {"code": "PB", "name": "Punjab", "name_hi": "पंजाब"},
    {"code": "RJ", "name": "Rajasthan", "name_hi": "राजस्थान"},
    {"code": "SK", "name": "Sikkim", "name_hi": "सिक्किम"},
    {"code": "TN", "name": "Tamil Nadu", "name_hi": "तमिलनाडु"},
    {"code": "TG", "name": "Telangana", "name_hi": "तेलंगाना"},
    {"code": "TR", "name": "Tripura", "name_hi": "त्रिपुरा"},
    {"code": "UP", "name": "Uttar Pradesh", "name_hi": "उत्तर प्रदेश"},
    {"code": "UT", "name": "Uttarakhand", "name_hi": "उत्तराखंड"},
    {"code": "WB", "name": "West Bengal", "name_hi": "पश्चिम बंगाल"}
]

# Sample districts for major states (can be expanded)
STATE_DISTRICTS = {
    "UP": [
        {"district_code": "UP01", "district_name": "Agra", "district_name_hi": "आगरा", "latitude": 27.1767, "longitude": 78.0081},
        {"district_code": "UP02", "district_name": "Aligarh", "district_name_hi": "अलीगढ़", "latitude": 27.8974, "longitude": 78.0880},
        {"district_code": "UP03", "district_name": "Allahabad", "district_name_hi": "इलाहाबाद", "latitude": 25.4358, "longitude": 81.8463},
        {"district_code": "UP04", "district_name": "Ambedkar Nagar", "district_name_hi": "अंबेडकर नगर", "latitude": 26.4050, "longitude": 82.6986},
        {"district_code": "UP05", "district_name": "Amethi", "district_name_hi": "अमेठी", "latitude": 26.1544, "longitude": 81.8084},
        {"district_code": "UP49", "district_name": "Lucknow", "district_name_hi": "लखनऊ", "latitude": 26.8467, "longitude": 80.9462},
        {"district_code": "UP50", "district_name": "Maharajganj", "district_name_hi": "महाराजगंज", "latitude": 27.1441, "longitude": 83.5599}
    ],
    "MH": [
        {"district_code": "MH01", "district_name": "Mumbai", "district_name_hi": "मुंबई", "latitude": 19.0760, "longitude": 72.8777},
        {"district_code": "MH02", "district_name": "Pune", "district_name_hi": "पुणे", "latitude": 18.5204, "longitude": 73.8567},
        {"district_code": "MH03", "district_name": "Nagpur", "district_name_hi": "नागपुर", "latitude": 21.1458, "longitude": 79.0882},
        {"district_code": "MH04", "district_name": "Nashik", "district_name_hi": "नासिक", "latitude": 19.9975, "longitude": 73.7898},
        {"district_code": "MH05", "district_name": "Thane", "district_name_hi": "ठाणे", "latitude": 19.2183, "longitude": 72.9781}
    ],
    "KA": [
        {"district_code": "KA01", "district_name": "Bengaluru Urban", "district_name_hi": "बेंगलुरु शहरी", "latitude": 12.9716, "longitude": 77.5946},
        {"district_code": "KA02", "district_name": "Mysuru", "district_name_hi": "मैसूरु", "latitude": 12.2958, "longitude": 76.6394},
        {"district_code": "KA03", "district_name": "Mangaluru", "district_name_hi": "मंगलुरु", "latitude": 12.9141, "longitude": 74.8560},
        {"district_code": "KA04", "district_name": "Hubli", "district_name_hi": "हुबली", "latitude": 15.3647, "longitude": 75.1240},
        {"district_code": "KA05", "district_name": "Belgaum", "district_name_hi": "बेलगाम", "latitude": 15.8497, "longitude": 74.4977}
    ],
    "TN": [
        {"district_code": "TN01", "district_name": "Chennai", "district_name_hi": "चेन्नई", "latitude": 13.0827, "longitude": 80.2707},
        {"district_code": "TN02", "district_name": "Coimbatore", "district_name_hi": "कोयंबटूर", "latitude": 11.0168, "longitude": 76.9558},
        {"district_code": "TN03", "district_name": "Madurai", "district_name_hi": "मदुरै", "latitude": 9.9252, "longitude": 78.1198},
        {"district_code": "TN04", "district_name": "Tiruchirappalli", "district_name_hi": "तिरुचिरापल्ली", "latitude": 10.7905, "longitude": 78.7047},
        {"district_code": "TN05", "district_name": "Salem", "district_name_hi": "सेलम", "latitude": 11.6643, "longitude": 78.1460}
    ],
    "RJ": [
        {"district_code": "RJ01", "district_name": "Jaipur", "district_name_hi": "जयपुर", "latitude": 26.9124, "longitude": 75.7873},
        {"district_code": "RJ02", "district_name": "Jodhpur", "district_name_hi": "जोधपुर", "latitude": 26.2389, "longitude": 73.0243},
        {"district_code": "RJ03", "district_name": "Udaipur", "district_name_hi": "उदयपुर", "latitude": 24.5854, "longitude": 73.7125},
        {"district_code": "RJ04", "district_name": "Kota", "district_name_hi": "कोटा", "latitude": 25.2138, "longitude": 75.8648},
        {"district_code": "RJ05", "district_name": "Bikaner", "district_name_hi": "बीकानेर", "latitude": 28.0229, "longitude": 73.3119}
    ],
    "GJ": [
        {"district_code": "GJ01", "district_name": "Ahmedabad", "district_name_hi": "अहमदाबाद", "latitude": 23.0225, "longitude": 72.5714},
        {"district_code": "GJ02", "district_name": "Surat", "district_name_hi": "सूरत", "latitude": 21.1702, "longitude": 72.8311},
        {"district_code": "GJ03", "district_name": "Vadodara", "district_name_hi": "वडोदरा", "latitude": 22.3072, "longitude": 73.1812},
        {"district_code": "GJ04", "district_name": "Rajkot", "district_name_hi": "राजकोट", "latitude": 22.3039, "longitude": 70.8022},
        {"district_code": "GJ05", "district_name": "Gandhinagar", "district_name_hi": "गांधीनगर", "latitude": 23.2156, "longitude": 72.6369}
    ],
    "WB": [
        {"district_code": "WB01", "district_name": "Kolkata", "district_name_hi": "कोलकाता", "latitude": 22.5726, "longitude": 88.3639},
        {"district_code": "WB02", "district_name": "Howrah", "district_name_hi": "हावड़ा", "latitude": 22.5958, "longitude": 88.2636},
        {"district_code": "WB03", "district_name": "Darjeeling", "district_name_hi": "दार्जिलिंग", "latitude": 27.0410, "longitude": 88.2663},
        {"district_code": "WB04", "district_name": "Siliguri", "district_name_hi": "सिलीगुड़ी", "latitude": 26.7271, "longitude": 88.3953},
        {"district_code": "WB05", "district_name": "Durgapur", "district_name_hi": "दुर्गापुर", "latitude": 23.5204, "longitude": 87.3119}
    ],
    "BR": [
        {"district_code": "BR01", "district_name": "Patna", "district_name_hi": "पटना", "latitude": 25.5941, "longitude": 85.1376},
        {"district_code": "BR02", "district_name": "Gaya", "district_name_hi": "गया", "latitude": 24.7955, "longitude": 84.9994},
        {"district_code": "BR03", "district_name": "Bhagalpur", "district_name_hi": "भागलपुर", "latitude": 25.2425, "longitude": 86.9842},
        {"district_code": "BR04", "district_name": "Muzaffarpur", "district_name_hi": "मुजफ्फरपुर", "latitude": 26.1225, "longitude": 85.3906},
        {"district_code": "BR05", "district_name": "Darbhanga", "district_name_hi": "दरभंगा", "latitude": 26.1542, "longitude": 85.8918}
    ],
    "MP": [
        {"district_code": "MP01", "district_name": "Bhopal", "district_name_hi": "भोपाल", "latitude": 23.2599, "longitude": 77.4126},
        {"district_code": "MP02", "district_name": "Indore", "district_name_hi": "इंदौर", "latitude": 22.7196, "longitude": 75.8577},
        {"district_code": "MP03", "district_name": "Gwalior", "district_name_hi": "ग्वालियर", "latitude": 26.2183, "longitude": 78.1828},
        {"district_code": "MP04", "district_name": "Jabalpur", "district_name_hi": "जबलपुर", "latitude": 23.1815, "longitude": 79.9864},
        {"district_code": "MP05", "district_name": "Ujjain", "district_name_hi": "उज्जैन", "latitude": 23.1765, "longitude": 75.7885}
    ]
}

def get_all_states():
    """Return list of all Indian states"""
    return INDIAN_STATES

def get_districts_for_state(state_code: str):
    """Return districts for a given state"""
    return STATE_DISTRICTS.get(state_code, [])
