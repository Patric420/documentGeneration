from typing import Dict, List

DOCUMENT_SCHEMAS: Dict[str, Dict[str, List[str]]] = {
    "NDA": {
        "required": [
            "Company_Name",
            "Location",
            "Effective_Date",
            "Company_CIN",
            "Company_Registered_Office",
            "Managing_Director_Name",
            "Managing_Director_DIN",
            "Managing_Director_Aadhaar",
            "Board_Resolution_Date",
            "Contractor_Name",
            "Contractor_Father_Name",
            "Contractor_Address",
            "Contractor_Aadhaar",
            "ICA_Date",
            "Term",
            "Protection_Period",
            "Jurisdiction"
        ],
        "optional": []
    },
    "Independent_Contractor_Agreement": {
        "required": [
            "Effective_Date",
            "Location",
            "Company_Name",
            "Company_CIN",
            "Company_Registered_Office",
            "Managing_Director_Name",
            "Managing_Director_DIN",
            "Managing_Director_Aadhaar",
            "Board_Resolution_Date",
            "Contractor_Name",
            "Contractor_Father_Name",
            "Contractor_Address",
            "Contractor_Aadhaar",
            "Role",
            "Duration",
            "Notice_Period",
            "Contractor_Fee",
            "Confidentiality_Period",
            "Non_Compete_Period",
            "Non_Solicitation_Period",
            "Jurisdiction"
        ],
        "optional": []
    },
    "Offer_Letter": {
        "required": ["Name", "Company", "Position", "Start_Date", "Salary"],
        "optional": ["Manager_Name", "Response_Date", "HR_Manager", "Benefits_Description"]
    },
    "Contract": {
        "required": [
            "Client_Name", "Company", "Contract_Creation_Date",
            "Service_Description", "Payment_Amount", "Start_Date", "End_Date"
        ],
        "optional": ["Payment_Schedule", "Termination_Clause"]
    },
    "MOU": {
        "required": ["PartyA_Name", "PartyB_Name", "Date", "Purpose", "Term", "Jurisdiction"],
        "optional": ["Confidentiality", "Termination_Clause", "Governing_Law"]
    },
    "IP_Agreement": {
        "required": ["Name", "Company", "Date", "Term", "Jurisdiction"],
        "optional": ["IP_Description", "Governing_Law"]
    },
    "Onboarding_Letter": {
        "required": [
            "Employee_Name",
            "Emp_ID",
            "Role",
            "Joining_Date",
            "Document_Date"
        ],
        "optional": []
    }
}