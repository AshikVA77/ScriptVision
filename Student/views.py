from django.shortcuts import get_object_or_404, render,redirect
from Student.models import *
from Teacher.models import *
from Admin.models import *
from Guest.models import *
import os

from io import BytesIO
import os

from django.http import FileResponse
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether
)

from django.http import FileResponse, Http404

# Create your views here.
def Studenthome(request):
    student_id = request.session["user_id"]

    result = tbl_result.objects.filter(
        stdexam__student_id=student_id,
        published=True
    ).first()

    return render(
        request,
        "Student/Studenthome.html",
        {
            "result": result
        }
    )

def Logout(request):
    request.session.flush()
    return redirect("Guest:index")


def ViewResult(request):

    student_id = request.session["user_id"]

    results = tbl_result.objects.filter(
        stdexam__student__student_id=student_id
    ).select_related(
        "stdexam__exam__subject"
    )

    return render(
        request,
        "Student/ResultView.html",
        {
            "results": results
        }
    )

def SubjectResult(request, subject_id):

    student_id = request.session["user_id"]

    evaluations = tbl_evaluation.objects.filter(
        answerscript__stdexam__student__student_id=student_id,
        answerscript__stdexam__exam__subject_id=subject_id
    ).select_related(
        "question",
        "answerscript__stdexam__exam__subject"
    )

    subject = tbl_subject.objects.filter(
        subject_id=subject_id
    ).first()

    return render(
        request,
        "Student/SubjectResult.html",
        {
            "evaluations": evaluations,
            "subject": subject
        }
    )
    

def Aifeedback(request, id):
    evaluation = get_object_or_404(
        tbl_evaluation,
        evaluation_id=id
    )

    return render(
        request,
        "Student/AIFeedback.html",
        {
            "evaluation": evaluation
        }
    )

def Report(request, id):

    student = get_object_or_404(
        tbl_student,
        student_id=request.session["user_id"]
    )

    result = get_object_or_404(
        tbl_result,
        result_id=id
    )

    evaluations = tbl_evaluation.objects.filter(
        answerscript__stdexam=result.stdexam
    )

    return render(
        request,
        "Student/Report.html",
        {
            "student": student,
            "result": result,
            "evaluations": evaluations
        }
    )

def SelectSubject(request):

    if request.session.get("user_type") != "student":
        return redirect("Guest:Login")

    student_id = request.session.get("user_id")

    student = tbl_student.objects.filter(
        student_id=student_id
    ).first()

    if not student:
        return redirect("Guest:Login")

    department = tbl_department.objects.filter(
        dept_code=student.student_department
    ).first()

    if not department:
        return render(
            request,
            "Student/SelectSubject.html",
            {
                "subjects": [],
                "enrolled_subjects": [],
                "error": "Your department is not configured."
            }
        )

    # Get subjects already selected by the student
    enrolled_subjects = tbl_student_subject.objects.filter(
        student=student,
        status="Active"
    ).select_related("subject")

    # Get IDs of already selected subjects
    enrolled_subject_ids = enrolled_subjects.values_list(
        "subject__pk",
        flat=True
        )

    # Show only active subjects not already selected
    subjects = tbl_subject.objects.filter(
        subject_department=department,
        subject_status="Active"
    ).exclude(
        subject_id__in=enrolled_subject_ids
    )

    if request.method == "POST":

        subject_id = request.POST.get("subject")

        subject = subjects.filter(
            subject_id=subject_id
        ).first()

        if not subject:
            return render(
                request,
                "Student/SelectSubject.html",
                {
                    "subjects": subjects,
                    "enrolled_subjects": enrolled_subjects,
                    "error": "Invalid subject selected."
                }
            )

        tbl_student_subject.objects.get_or_create(
            student=student,
            subject=subject
        )

        return redirect("Student:SelectSubject")

    return render(
        request,
        "Student/SelectSubject.html",
        {
            "subjects": subjects,
            "enrolled_subjects": enrolled_subjects
        }
    )
    

def StudyMaterials(request):

    if request.session.get("user_type") != "student":
        return redirect("Guest:Login")

    departments = tbl_department.objects.all().order_by("dept_name")

    material_titles = []
    materials = []
    error = None

    selected_department = ""
    selected_title = ""

    # -----------------------------------------
    # DOWNLOAD SELECTED MATERIAL
    # -----------------------------------------

    download_id = request.GET.get("download")

    if download_id:

        material = tbl_studymaterial.objects.filter(
            material_id=download_id,
            material_status="Active"
        ).first()

        if not material or not material.material_file:
            raise Http404("Study material not found.")

        file_name = os.path.basename(
            material.material_file.name
        )

        try:
            file = material.material_file.open("rb")
        except FileNotFoundError:
            raise Http404("The uploaded file is missing from the server.")

        return FileResponse(
            file,
            as_attachment=True,
            filename=file_name
        )

    # -----------------------------------------
    # HANDLE DEPARTMENT AND MATERIAL SELECTION
    # -----------------------------------------

    if request.method == "POST":

        selected_department = request.POST.get(
            "department", ""
        )

        selected_title = request.POST.get(
            "material_title", ""
        ).strip()

        # Validate selected department
        department = departments.filter(
            dept_id=selected_department
        ).first()

        if not department:
            error = "Please select a valid department."

        else:

            # Load only materials belonging to selected department
            material_titles = tbl_studymaterial.objects.filter(
                material_department_id=selected_department,
                material_status="Active"
            ).values_list(
                "material_title",
                flat=True
            ).distinct().order_by("material_title")

            # Find materials only when Find Material is clicked
            if "find_material" in request.POST:

                if not selected_title:
                    error = "Please select a material."

                else:
                    materials = tbl_studymaterial.objects.filter(
                        material_department_id=selected_department,
                        material_title=selected_title,
                        material_status="Active"
                    ).order_by("-uploaded_date")

                    if not materials.exists():
                        error = "No material found for the selected department and title."

    return render(
        request,
        "Student/StudyMaterials.html",
        {
            "departments": departments,
            "material_titles": material_titles,
            "materials": materials,
            "error": error,
            "selected_department": selected_department,
            "selected_title": selected_title
        }
    )
    
def StudentFeedback(request):

    # Check student login
    if request.session.get("user_type") != "student":
        return redirect("Guest:Login")

    student_id = request.session.get("user_id")

    if not student_id:
        return redirect("Guest:Login")

    student = tbl_student.objects.filter(
        student_id=student_id
    ).first()

    if not student:
        return redirect("Guest:Login")

    # Get results belonging to the logged-in student
    student_results = tbl_result.objects.filter(
        stdexam__student=student
    ).select_related(
        "stdexam",
        "stdexam__exam",
        "stdexam__exam__subject"
    ).order_by("-stdexam__exam__exam_date")

    error = None

    # Submit feedback
    if request.method == "POST":

        result_id = request.POST.get("result_id")
        student_comment = request.POST.get("student_comment", "").strip()

        if not result_id:
            error = "Please select an exam."

        elif not student_comment:
            error = "Please enter your feedback message."

        else:
            # Ensure the selected result belongs to this student
            result = student_results.filter(
                result_id=result_id
            ).first()

            if not result:
                error = "Invalid exam selection."

            else:
                tbl_studentfeedback.objects.create(
                    student=student,
                    result=result,
                    student_comment=student_comment,
                    status="Pending"
                )

                return redirect("Student:StudentFeedback")

    # Get recent feedback
    feedback_list = tbl_studentfeedback.objects.filter(
        student=student
    ).select_related(
        "result",
        "result__stdexam",
        "result__stdexam__exam"
    ).order_by("-created_at")

    context = {
        "student_results": student_results,
        "feedback_list": feedback_list,
        "error": error,
    }

    return render(
        request,
        "Student/StudentFeedback.html",
        context
    )
    
def StudentProfile(request):
    if request.session.get("user_type") != "student":
        return redirect("Guest:Login")

    student_id = request.session.get("user_id")

    if not student_id:
        return redirect("Guest:Login")

    student = tbl_student.objects.filter(student_id=student_id).first()

    if not student:
        return redirect("Guest:Login")

    return render(request, "Student/StudentProfile.html", {
        "student": student
    })
    
def EditStudentProfile(request):
    if request.session.get("user_type") != "student":
        return redirect("Guest:Login")

    student_id = request.session.get("user_id")

    if not student_id:
        return redirect("Guest:Login")

    student = tbl_student.objects.filter(student_id=student_id).first()

    if not student:
        return redirect("Guest:Login")

    if request.method == "POST":
        student.student_name = request.POST.get("student_name", "").strip()
        student.student_email = request.POST.get("student_email", "").strip()
        student.student_phone = request.POST.get("student_phone", "").strip()

        if request.FILES.get("student_profile_pic"):
            student.student_profile_pic = request.FILES.get("student_profile_pic")

        student.save()

        return redirect("Student:StudentProfile")

    return render(request, "Student/EditStudentProfile.html", {
        "student": student
    })
    
def DownloadResult(request):

    if request.session.get("user_type") != "student":
        return redirect("Guest:Login")

    student_id = request.session.get("user_id")

    if not student_id:
        return redirect("Guest:Login")

    student = tbl_student.objects.filter(
        student_id=student_id
    ).first()

    if not student:
        return redirect("Guest:Login")

    results = tbl_result.objects.filter(
        stdexam__student=student
    ).select_related(
        "stdexam",
        "stdexam__exam",
        "stdexam__exam__subject"
    )

    exam_series = results.values_list(
        "stdexam__exam__exam_type",
        flat=True
    ).distinct().order_by(
        "stdexam__exam__exam_type"
    )

    exam_type = request.GET.get("exam_type")

    if exam_type:

        selected_results = results.filter(
            stdexam__exam__exam_type=exam_type
        ).order_by(
            "stdexam__exam__subject__subject_name"
        )

        if not selected_results.exists():

            return render(
                request,
                "Student/DownloadResult.html",
                {
                    "student": student,
                    "exam_series": exam_series,
                    "error": "No results found for the selected exam series."
                }
            )

        # ---------------------------------------------------------
        # PDF SETUP
        # ---------------------------------------------------------

        buffer = BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=45
        )

        styles = getSampleStyleSheet()

        # ---------------------------------------------------------
        # COLORS
        # ---------------------------------------------------------

        purple = colors.HexColor("#8B5CF6")
        purple_dark = colors.HexColor("#6D28D9")
        purple_light = colors.HexColor("#F3EEFF")

        dark = colors.HexColor("#171421")
        text = colors.HexColor("#34303D")
        muted = colors.HexColor("#77727F")

        border = colors.HexColor("#E5E0EC")
        light_bg = colors.HexColor("#FAF9FC")
        white = colors.white

        # ---------------------------------------------------------
        # STYLES
        # ---------------------------------------------------------

        title_style = ParagraphStyle(
            "SVTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=dark,
            alignment=TA_CENTER,
            spaceAfter=3
        )

        subtitle_style = ParagraphStyle(
            "SVSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=muted,
            alignment=TA_CENTER
        )

        section_style = ParagraphStyle(
            "SVSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=purple_dark,
            spaceBefore=4,
            spaceAfter=7
        )

        normal_style = ParagraphStyle(
            "SVNormal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=text
        )

        small_style = ParagraphStyle(
            "SVSmall",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=muted
        )

        footer_style = ParagraphStyle(
            "SVFooter",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=muted,
            alignment=TA_CENTER
        )

        # ---------------------------------------------------------
        # STORY
        # ---------------------------------------------------------

        story = []

        # ---------------------------------------------------------
        # LOGO
        # ---------------------------------------------------------

        logo_path = os.path.join(
            settings.BASE_DIR,
            "Guest",
            "static",
            "Main",
            "img",
            "scriptvisionlogo.png"
        )

        if os.path.exists(logo_path):

            logo = Image(
                logo_path,
                width=51,
                height=51
            )

            logo.hAlign = "CENTER"

            story.append(logo)
            story.append(Spacer(1, 5))

        # ---------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "SCRIPT VISION",
                title_style
            )
        )

        story.append(
            Paragraph(
                "EXAMINATION RESULT",
                subtitle_style
            )
        )

        story.append(Spacer(1, 8))

        # Purple divider
        divider = Table(
            [[""]],
            colWidths=[520]
        )

        divider.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    purple
                ),
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    0,
                    purple
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1
                )
            ])
        )

        story.append(divider)
        story.append(Spacer(1, 16))

        # ---------------------------------------------------------
        # STUDENT INFORMATION
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "STUDENT INFORMATION",
                section_style
            )
        )

        first_result = selected_results.first()

        exam_date = first_result.stdexam.exam.exam_date
        academic_year = first_result.stdexam.exam.academic_year

        student_data = [
            [
                Paragraph("<b>Student Name</b>", normal_style),
                Paragraph(str(student.student_name), normal_style),

                Paragraph("<b>Student ID</b>", normal_style),
                Paragraph(str(student.student_id), normal_style)
            ],
            [
                Paragraph("<b>Department</b>", normal_style),
                Paragraph(str(student.student_department), normal_style),

                Paragraph("<b>Exam Series</b>", normal_style),
                Paragraph(str(exam_type), normal_style)
            ],
            [
                Paragraph("<b>Academic Year</b>", normal_style),
                Paragraph(str(academic_year), normal_style),

                Paragraph("<b>Exam Date</b>", normal_style),
                Paragraph(
                    exam_date.strftime("%d %B %Y"),
                    normal_style
                )
            ]
        ]

        student_table = Table(
            student_data,
            colWidths=[85, 160, 85, 160],
            rowHeights=[30, 30, 30]
        )

        student_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    light_bg
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    border
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    border
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        story.append(student_table)
        story.append(Spacer(1, 18))

        # ---------------------------------------------------------
        # RESULT SUMMARY
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "RESULT SUMMARY",
                section_style
            )
        )

        summary_data = [
            [
                Paragraph(
                    "<b>SUBJECTS EVALUATED</b>",
                    small_style
                ),
                Paragraph(
                    "<b>RESULT STATUS</b>",
                    small_style
                ),
                Paragraph(
                    "<b>EVALUATION METHOD</b>",
                    small_style
                )
            ],
            [
                Paragraph(
                    f"<font size='16'><b>{selected_results.count()}</b></font>",
                    normal_style
                ),
                Paragraph(
                    "<font size='10'><b>Completed</b></font>",
                    normal_style
                ),
                Paragraph(
                    "<font size='9'><b>AI + Teacher Evaluation</b></font>",
                    normal_style
                )
            ]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[170, 150, 170],
            rowHeights=[22, 38]
        )

        summary_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    purple_light
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor("#DDD2F7")
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#E7DFF7")
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(summary_table)
        story.append(Spacer(1, 18))

        # ---------------------------------------------------------
        # SUBJECT-WISE RESULT
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "SUBJECT-WISE RESULT",
                section_style
            )
        )

        result_data = [
            [
                Paragraph("<b>Subject</b>", normal_style),
                Paragraph("<b>AI Mark</b>", normal_style),
                Paragraph("<b>Teacher Mark</b>", normal_style),
                Paragraph("<b>Final Mark</b>", normal_style),
                Paragraph("<b>Grade</b>", normal_style)
            ]
        ]

        for result in selected_results:

            evaluations = tbl_evaluation.objects.filter(
                answerscript__stdexam=result.stdexam
            )

            teacher_mark = 0

            for evaluation in evaluations:

                if evaluation.teacher_score is not None:
                    teacher_mark += evaluation.teacher_score

            ai_mark = result.total_ai_marks or 0
            final_mark = result.total_final_marks or 0
            grade = result.grade if result.grade else "-"

            subject_name = (
                result.stdexam.exam.subject.subject_name
            )

            result_data.append(
                [
                    Paragraph(
                        str(subject_name),
                        normal_style
                    ),
                    Paragraph(
                        str(ai_mark),
                        normal_style
                    ),
                    Paragraph(
                        str(teacher_mark),
                        normal_style
                    ),
                    Paragraph(
                        str(final_mark),
                        normal_style
                    ),
                    Paragraph(
                        f"<b>{grade}</b>",
                        normal_style
                    )
                ]
            )

        result_table = Table(
            result_data,
            colWidths=[190, 75, 85, 75, 60],
            repeatRows=1
        )

        result_table.setStyle(
            TableStyle([
                # Header
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    purple_dark
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    white
                ),

                # Body
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    white
                ),

                # Alternating rows
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [white, light_bg]
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    border
                ),

                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    border
                ),

                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "CENTER"
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(result_table)
        story.append(Spacer(1, 18))

        # ---------------------------------------------------------
        # GRADING SCALE
        # ---------------------------------------------------------

        story.append(
            Paragraph(
                "GRADING SCALE",
                section_style
            )
        )

        grading_data = [
            [
                Paragraph("<b>A+</b>", normal_style),
                Paragraph("Excellent", normal_style),

                Paragraph("<b>A</b>", normal_style),
                Paragraph("Very Good", normal_style),

                Paragraph("<b>B+</b>", normal_style),
                Paragraph("Good", normal_style)
            ],
            [
                Paragraph("<b>B</b>", normal_style),
                Paragraph("Satisfactory", normal_style),

                Paragraph("<b>C</b>", normal_style),
                Paragraph("Average", normal_style),

                Paragraph("<b>P</b>", normal_style),
                Paragraph("Pass", normal_style)
            ],
            [
                Paragraph("<b>F</b>", normal_style),
                Paragraph("Fail", normal_style),

                "",
                "",
                "",
                ""
            ]
        ]

        grading_table = Table(
            grading_data,
            colWidths=[35, 120, 35, 120, 35, 120]
        )

        grading_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    light_bg
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    border
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    border
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        story.append(grading_table)
        story.append(Spacer(1, 20))

        # ---------------------------------------------------------
        # FOOTER CONTENT
        # ---------------------------------------------------------

        footer_line = Table(
            [[""]],
            colWidths=[520]
        )

        footer_line.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    border
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0.5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0.5
                )
            ])
        )

        story.append(footer_line)
        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "This is a computer-generated result document.",
                footer_style
            )
        )

        story.append(
            Paragraph(
                "Generated by ScriptVision",
                footer_style
            )
        )

        # ---------------------------------------------------------
        # PAGE NUMBER
        # ---------------------------------------------------------

        def add_page_design(canvas, doc):

            canvas.saveState()

            # -----------------------------------------
            # OUTER PURPLE BORDER
            # -----------------------------------------

            canvas.setStrokeColor(
                colors.HexColor("#8B5CF6")
            )

            canvas.setLineWidth(1.2)

            canvas.rect(
                18,
                18,
                A4[0] - 36,
                A4[1] - 36
            )

            # -----------------------------------------
            # INNER SUBTLE BORDER
            # -----------------------------------------

            canvas.setStrokeColor(
                colors.HexColor("#E9DDFB")
            )

            canvas.setLineWidth(0.4)

            canvas.rect(
                23,
                23,
                A4[0] - 46,
                A4[1] - 46
            )

            # -----------------------------------------
            # PAGE NUMBER
            # -----------------------------------------

            canvas.setFont(
                "Helvetica",
                7
            )

            canvas.setFillColor(
                colors.HexColor("#77727F")
            )

            canvas.drawRightString(
                A4[0] - 35,
                22,
                f"Page {doc.page}"
            )

            canvas.restoreState()

        # ---------------------------------------------------------
        # BUILD PDF
        # ---------------------------------------------------------

        pdf.build(
            story,
            onFirstPage=add_page_design,
            onLaterPages=add_page_design
        )

        buffer.seek(0)

        filename = (
            exam_type.replace(" ", "_")
            + "_Result.pdf"
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename=filename
        )

    # ---------------------------------------------------------
    # NORMAL DOWNLOAD RESULT PAGE
    # ---------------------------------------------------------

    return render(
        request,
        "Student/DownloadResult.html",
        {
            "student": student,
            "exam_series": exam_series
        }
    )