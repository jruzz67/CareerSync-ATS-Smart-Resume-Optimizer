import fitz  # PyMuPDF
import re
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_pdf_resume(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        
        logger.debug(f"Parsed text preview: {text[:100]}...")

        sections = {
            "skills": [],
            "experience": [],
            "education": [],
            "contact": [],
            "projects": [],
            "achievements": [],
            "certifications": []
        }

        section_patterns = {
            "skills": r"^(skills|technical skills|core competencies|technologies)\s*$",
            "experience": r"^(experience|work experience|professional experience)\s*$",
            "education": r"^(education|academic background)\s*$",
            "contact": r"^(contact|contact information|personal information)\s*$",
            "projects": r"^(projects|project experience)\s*$",
            "achievements": r"^(achievements|awards|honors)\s*$",
            "certifications": r"^(certifications|certificates)\s*$"
        }

        lines = text.split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for section, pattern in section_patterns.items():
                if re.match(pattern, line, re.I):
                    current_section = section
                    break
            else:
                if current_section:
                    sections[current_section].append(line)

        # Clean up skills section
        if sections["skills"]:
            skills_text = " ".join(sections["skills"])
            skills = re.split(r"[,\n•\-]+", skills_text)
            sections["skills"] = [s.strip() for s in skills if s.strip()]

        # Format experience section (group by job roles)
        if sections["experience"]:
            experience = []
            current_job = []
            for line in sections["experience"]:
                if re.match(r"^\d{4}\s*-\s*\d{4}|Present", line, re.I):
                    if current_job:
                        experience.append(" ".join(current_job))
                        current_job = []
                current_job.append(line)
            if current_job:
                experience.append(" ".join(current_job))
            sections["experience"] = experience

        # Remove empty entries
        for section in sections:
            sections[section] = [item for item in sections[section] if item]

        logger.debug(f"Parsed sections: {sections}")
        return text, sections
    except Exception as e:
        logger.error(f"PDF parsing error: {str(e)}")
        raise RuntimeError(f"Failed to parse PDF: {str(e)}")
