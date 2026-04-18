import os
from fpdf import FPDF

class PDFPlan(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'StudyOS - AI Study Plan', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(plan_df, days, hours, crash_mode):
    pdf = PDFPlan()
    pdf.add_page()
    
    # Metadata
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 8, f"Duration: {days} Days | Study Time: {hours} Hours/Day", 0, 1)
    if crash_mode:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 8, "CRASH MODE ENABLED - No Revision Slots", 0, 1)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    if plan_df is None or plan_df.empty:
        pdf.cell(0, 10, "No topics planned.", 0, 1)
        return bytes(pdf.output(dest='S'))

    # Group by Day
    sched = plan_df[~plan_df["Type"].isin(["Known", "Overflow"])]
    day_order = sorted(
        sched["Day"].unique(),
        key=lambda d: int(d.replace("Day ","")) if d.replace("Day ","").isdigit() else 999
    )

    for day in day_order:
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, f"{day}", 0, 1)
        
        items = sched[sched["Day"] == day]
        for _, r in items.iterrows():
            pdf.set_font('helvetica', 'B', 11)
            # type
            is_rev = r['Type'] == 'Revision'
            prefix = "[Revise]" if is_rev else "[Study]"
            idx = r['Block']
            topic = r['Topic']
            subj = r['Subject']
            diff = r.get('Difficulty', '')

            pdf.cell(20, 8, str(idx), 0, 0)
            pdf.cell(40, 8, f"{prefix} {diff}", 0, 0)
            
            # Use multi_cell for topic to handle long text
            # Encode correctly to avoid FPDF escaping errors
            topic_clean = topic.encode('latin-1', 'replace').decode('latin-1')
            subj_clean = subj.encode('latin-1', 'replace').decode('latin-1')
            
            pdf.cell(0, 8, f"{topic_clean} ({subj_clean})", 0, 1)

        pdf.ln(5)

    # Overflow
    overflow = plan_df[plan_df["Type"] == "Overflow"]
    if not overflow.empty:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, "Overflow Topics (Did not fit in plan)", 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        for _, r in overflow.iterrows():
            pdf.set_font('helvetica', '', 11)
            topic = r['Topic'].encode('latin-1', 'replace').decode('latin-1')
            subj = r['Subject'].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 8, f"- {topic} ({subj})", 0, 1)

    return bytes(pdf.output(dest='S'))
