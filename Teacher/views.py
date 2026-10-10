import os
import fitz
from django.shortcuts import get_object_or_404, render, redirect
from Admin.models import *
from Student.models import *
from Guest.models import *
from Teacher.models import *

from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from django.core.mail import EmailMultiAlternatives
from django.templatetags.static import static
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage

try:
    from AI.exam_evaluator import evaluate_exam
except Exception as e:
    print("AI IMPORT ERROR:", e)
    evaluate_exam = None

# Create your views here.

def Teacherhome(request):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    return render(
        request,
        'Teacher/Teacherhome.html'
    )


def CreateExam(request):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    teacher = tbl_teacher.objects.filter(
        teacher_id=teacher_id
    ).first()

    if not teacher:
        return redirect("Guest:Login")

    if request.method == "POST":

        tbl_exam.objects.create(
            teacher_id=teacher_id,
            subject_id=request.POST.get("subject"),
            exam_name=request.POST.get("exam_name"),
            exam_type=request.POST.get("exam_type"),
            exam_date=request.POST.get("exam_date"),
            academic_year=request.POST.get("academic_year"),
            total_marks=request.POST.get("total_marks")
        )

        return redirect("Teacher:Teacherhome")

    subjects = tbl_subject.objects.filter(
        subject_department__dept_code=teacher.teacher_department,
        subject_status="Active"
    )

    return render(
        request,
        "Teacher/CreateExam.html",
        {
            "subjects": subjects
        }
    )
    
def EvaluateScript(request, stdexam_id):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    # ---------------------------------------------
    # Get student's exam
    # ---------------------------------------------

    stdexam = tbl_stdexam.objects.filter(
        stdexam_id=stdexam_id,
        exam__teacher_id=teacher_id
    ).select_related(
        "student",
        "exam",
        "exam__subject"
    ).first()

    if not stdexam:
        return redirect("Teacher:Teacherhome")

    # ---------------------------------------------
    # Get question-wise evaluations
    # ---------------------------------------------

    evaluations = tbl_evaluation.objects.filter(
        answerscript__stdexam=stdexam
    ).select_related(
        "question"
    ).order_by(
        "question__question_id"
    )

    # ---------------------------------------------
    # Save teacher marks
    # ---------------------------------------------

    if request.method == "POST":

        for evaluation in evaluations:

            mark = request.POST.get(
                f"teacher_mark_{evaluation.evaluation_id}"
            )

            if mark == "" or mark is None:
                continue

            try:
                teacher_mark = float(mark)

            except (ValueError, TypeError):
                continue

            # -----------------------------------------
            # Prevent invalid marks
            # -----------------------------------------

            if teacher_mark < 0:
                teacher_mark = 0

            if teacher_mark > evaluation.question.maximum_marks:
                teacher_mark = evaluation.question.maximum_marks

            # -----------------------------------------
            # Save teacher mark
            # -----------------------------------------

            evaluation.teacher_score = teacher_mark

            # Teacher mark becomes final mark
            evaluation.final_mark = teacher_mark

            evaluation.save()

        # ---------------------------------------------
        # Calculate overall result
        # ---------------------------------------------

        total_ai_marks = 0
        total_teacher_marks = 0
        total_final_marks = 0
        total_max_marks = 0

        for evaluation in evaluations:

            ai_mark = evaluation.ai_score or 0

            total_ai_marks += ai_mark

            total_max_marks += (
                evaluation.question.maximum_marks
            )

            if evaluation.teacher_score is not None:

                total_teacher_marks += (
                    evaluation.teacher_score
                )

                total_final_marks += (
                    evaluation.teacher_score
                )

            else:

                # Until teacher reviews the question,
                # AI mark remains as the final mark.
                total_final_marks += ai_mark

        # ---------------------------------------------
        # Calculate percentage
        # ---------------------------------------------

        percentage = 0

        if total_max_marks > 0:

            percentage = round(
                (
                    total_final_marks /
                    total_max_marks
                ) * 100,
                2
            )

        # ---------------------------------------------
        # Calculate grade
        # ---------------------------------------------

        if percentage >= 90:
            grade = "A+"

        elif percentage >= 80:
            grade = "A"

        elif percentage >= 70:
            grade = "B"

        elif percentage >= 60:
            grade = "C"

        elif percentage >= 50:
            grade = "D"

        else:
            grade = "F"

        # ---------------------------------------------
        # Update overall result
        # ---------------------------------------------

        tbl_result.objects.update_or_create(
            stdexam=stdexam,
            defaults={
                "total_ai_marks": round(
                    total_ai_marks,
                    2
                ),

                "total_teacher_marks": round(
                    total_teacher_marks,
                    2
                ),

                "total_final_marks": round(
                    total_final_marks,
                    2
                ),

                "grade": grade,

                "remarks": (
                    "Teacher evaluation completed."
                ),

                "published": False
            }
        )

        return redirect(
            "Teacher:EvaluateScript",
            stdexam_id=stdexam_id
        )

    # ---------------------------------------------
    # Display evaluation page
    # ---------------------------------------------

    return render(
        request,
        "Teacher/EvaluateScript.html",
        {
            "stdexam": stdexam,
            "evaluations": evaluations
        }
    )
    
def ExamResults(request):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    exams = tbl_exam.objects.filter(
        teacher_id=teacher_id
    ).select_related(
        "subject"
    ).order_by(
        "-exam_date"
    )

    return render(
        request,
        "Teacher/ExamResults.html",
        {
            "exams": exams
        }
    )
    
def ExamStudents(request, exam_id):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    exam = tbl_exam.objects.filter(
        exam_id=exam_id,
        teacher_id=teacher_id
    ).select_related(
        "subject"
    ).first()

    if not exam:
        return redirect("Teacher:ExamResults")

    students = tbl_stdexam.objects.filter(
        exam=exam
    ).select_related(
        "student"
    ).order_by(
        "student__student_name"
    )

    return render(
        request,
        "Teacher/ExamStudents.html",
        {
            "exam": exam,
            "students": students
        }
    )
    

def Questions(request):
    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    exams = tbl_exam.objects.filter(
        teacher_id=teacher_id
    )

    if request.method == "POST":
        exam_id = request.POST.get("exam")

        return redirect(
            "Teacher:AddQuestions",
            exam_id=exam_id
        )

    return render(request, "Teacher/Questions.html", {
        "exams": exams
    })

def AddQuestions(request, exam_id):
    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    exam = tbl_exam.objects.filter(
        exam_id=exam_id,
        teacher_id=teacher_id
    ).first()

    if not exam:
        return redirect("Teacher:Questions")

    if request.method == "POST":

        tbl_question.objects.create(
            exam=exam,
            question_number=request.POST.get("question_number"),
            question_text=request.POST.get("question_text"),
            model_answer=request.POST.get("model_answer"),
            keywords=request.POST.get("keywords"),
            maximum_marks=request.POST.get("maximum_marks")
        )

        return redirect(
            "Teacher:AddQuestions",
            exam_id=exam.exam_id
        )

    questions = tbl_question.objects.filter(
        exam=exam
    )

    return render(request, "Teacher/AddQuestions.html", {
        "exam": exam,
        "questions": questions
    })
def UploadScripts(request):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    exams = tbl_exam.objects.filter(
        teacher_id=teacher_id
    )

    if request.method == "POST":

        exam_id = request.POST.get("exam")

        if not exam_id:
            return render(
                request,
                "Teacher/UploadScripts.html",
                {
                    "exams": exams,
                    "error": "Please select an exam."
                }
            )

        # Move to student selection and upload page
        return redirect(
            "Teacher:SelectStudent",
            exam_id=exam_id
        )

    return render(
        request,
        "Teacher/UploadScripts.html",
        {
            "exams": exams
        }
    )


def SelectStudent(request, exam_id):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    # ---------------------------------------------
    # Check whether exam belongs to teacher
    # ---------------------------------------------

    exam = tbl_exam.objects.filter(
        exam_id=exam_id,
        teacher_id=teacher_id
    ).first()

    if not exam:
        return redirect("Teacher:UploadScripts")

    # ---------------------------------------------
    # Get students who selected this subject
    # ---------------------------------------------

    enrolled_students = tbl_student_subject.objects.filter(
        subject=exam.subject,
        status="Active"
    ).select_related(
        "student",
        "subject"
    )

    # ---------------------------------------------
    # POST: Student selection and script upload
    # ---------------------------------------------

    if request.method == "POST":

        student_id = request.POST.get("student")
        uploaded_file = request.FILES.get("answer_script")

        # -----------------------------------------
        # Check selected student
        # -----------------------------------------

        selected_student = enrolled_students.filter(
            student_id=student_id
        ).first()

        if not selected_student:
            return render(
                request,
                "Teacher/SelectStudent.html",
                {
                    "exam": exam,
                    "stdexams": enrolled_students,
                    "error": "Invalid student selected."
                }
            )

        # -----------------------------------------
        # Check uploaded file
        # -----------------------------------------

        if not uploaded_file:
            return render(
                request,
                "Teacher/SelectStudent.html",
                {
                    "exam": exam,
                    "stdexams": enrolled_students,
                    "selected_student": selected_student.student,
                    "error": "Please select an answer script."
                }
            )

        # -----------------------------------------
        # Check file type
        # -----------------------------------------

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        if extension not in [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png"
        ]:
            return render(
                request,
                "Teacher/SelectStudent.html",
                {
                    "exam": exam,
                    "stdexams": enrolled_students,
                    "selected_student": selected_student.student,
                    "error": (
                        "Only PDF, JPG, JPEG and PNG "
                        "files are allowed."
                    )
                }
            )

        # -----------------------------------------
        # Find or create student exam
        # -----------------------------------------

        stdexam = tbl_stdexam.objects.filter(
            student_id=student_id,
            exam_id=exam_id
        ).first()

        if not stdexam:
            stdexam = tbl_stdexam.objects.create(
                student_id=student_id,
                exam_id=exam_id,
                status="Pending"
            )

        # -----------------------------------------
        # Create answer script
        # -----------------------------------------

        answerscript = tbl_answerscript.objects.create(
            stdexam=stdexam,
            uploaded_file=uploaded_file,
            file_type=extension.replace(".", ""),
            status="Pending"
        )

        # -----------------------------------------
        # Calculate number of pages
        # -----------------------------------------

        if extension == ".pdf":

            pdf = fitz.open(
                answerscript.uploaded_file.path
            )

            answerscript.total_pages = len(pdf)

            pdf.close()

        else:
            answerscript.total_pages = 1

        answerscript.save()

        # =========================================
        # AI EVALUATION STARTS HERE
        # =========================================

        questions = tbl_question.objects.filter(
            exam=exam
        ).order_by(
            "question_id"
        )

        if questions.exists():

            print("DEBUG evaluate_exam:", repr(evaluate_exam))
            print("DEBUG type:", type(evaluate_exam))

            result = evaluate_exam(
                file_path=answerscript.uploaded_file.path,
                questions=questions
            )

            # -------------------------------------
            # Save question-wise evaluation
            # -------------------------------------

            for evaluation in result["evaluations"]:

                question = evaluation["question"]
                marks = evaluation["marks"]

                tbl_evaluation.objects.create(
                    answerscript=answerscript,
                    question=question,
                    page_number=evaluation["page_number"] or 0,
                    extracted_text=evaluation["extracted_text"],
                    similarity_score=evaluation["similarity"],
                    ai_score=marks["total_marks"],
                    teacher_score=None,
                    final_mark=marks["total_marks"],
                    feedback=evaluation["feedback"],
                    evaluation_status="Completed"
                )

            # -------------------------------------
            # Save overall result
            # -------------------------------------

            tbl_result.objects.update_or_create(
                stdexam=stdexam,
                defaults={
                    "total_ai_marks": result["total_ai_marks"],
                    "total_teacher_marks": None,
                    "total_final_marks": result["total_ai_marks"],
                    "grade": result["grade"],
                    "remarks": "AI evaluation completed.",
                    "published": False
                }
            )

            # -------------------------------------
            # Update answer script status
            # -------------------------------------

            answerscript.status = "Completed"
            answerscript.save()

            # -------------------------------------
            # Update student exam status
            # -------------------------------------

            stdexam.status = "Completed"
            stdexam.save()

        # =========================================
        # AI EVALUATION ENDS HERE
        # =========================================

        # Show success alert on SelectStudent.html.
        # After the teacher clicks OK, JavaScript
        # redirects to Teacherhome.
        messages.success(
            request,
            "Answer script uploaded and evaluated successfully!"
        )

        return redirect(
            "Teacher:SelectStudent",
            exam_id=exam_id
        )

    # ---------------------------------------------
    # GET: Display student selection and upload form
    # ---------------------------------------------

    return render(
        request,
        "Teacher/SelectStudent.html",
        {
            "exam": exam,
            "stdexams": enrolled_students
        }
    )

def Logout(request):

    request.session.flush()

    return redirect("Guest:index")

def TeacherFeedback(request):

    # Check teacher login
    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    if not teacher_id:
        return redirect("Guest:Login")

    teacher = tbl_teacher.objects.filter(
        teacher_id=teacher_id
    ).first()

    if not teacher:
        return redirect("Guest:Login")

    # Show only feedback for exams assigned to this teacher
    feedback_list = tbl_studentfeedback.objects.filter(
        result__stdexam__exam__teacher=teacher
    ).select_related(
        "student",
        "result",
        "result__stdexam",
        "result__stdexam__exam",
        "result__stdexam__exam__subject"
    ).order_by("-created_at")

    error = None

    # Submit teacher reply
    if request.method == "POST":

        feedback_id = request.POST.get("feedback_id")
        teacher_reply = request.POST.get("reply", "").strip()

        if not feedback_id:
            error = "Feedback not found."

        elif not teacher_reply:
            error = "Please enter a reply."

        else:
            # Confirm this feedback belongs to an exam assigned to this teacher
            feedback = feedback_list.filter(
                feedback_id=feedback_id
            ).first()

            if not feedback:
                error = "Invalid feedback selection."

            else:
                feedback.reply = teacher_reply
                feedback.status = "Replied"
                feedback.reply_date = timezone.now()
                feedback.save(
                    update_fields=["reply", "status", "reply_date"]
                )

                return redirect("Teacher:TeacherFeedback")

    context = {
        "feedback_list": feedback_list,
        "error": error,
    }

    return render(
        request,
        "Teacher/TeacherFeedback.html",
        context
    )
    
    
def TeacherProfile(request):
    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    if not teacher_id:
        return redirect("Guest:Login")

    teacher = tbl_teacher.objects.filter(teacher_id=teacher_id).first()

    if not teacher:
        return redirect("Guest:Login")

    return render(request, "Teacher/TeacherProfile.html", {
        "teacher": teacher
    })
    
def EditTeacherProfile(request):
    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    teacher_id = request.session.get("user_id")

    if not teacher_id:
        return redirect("Guest:Login")

    teacher = tbl_teacher.objects.filter(teacher_id=teacher_id).first()

    if not teacher:
        return redirect("Guest:Login")

    if request.method == "POST":
        teacher.teacher_name = request.POST.get("teacher_name", "").strip()
        teacher.teacher_email = request.POST.get("teacher_email", "").strip()
        teacher.teacher_phone = request.POST.get("teacher_phone", "").strip()

        if request.FILES.get("teacher_profile_pic"):
            teacher.teacher_profile_pic = request.FILES.get("teacher_profile_pic")

        teacher.save()

        return redirect("Teacher:TeacherProfile")

    return render(request, "Teacher/EditTeacherProfile.html", {
        "teacher": teacher
    })
    
    
def PublishExamResults(request, exam_id):

    if request.session.get("user_type") != "teacher":
        return redirect("Guest:Login")

    if request.method != "POST":
        return redirect("Teacher:ExamResults")

    teacher_id = request.session.get("user_id")

    exam = get_object_or_404(
        tbl_exam,
        exam_id=exam_id,
        teacher_id=teacher_id
    )

    results = tbl_result.objects.filter(
        stdexam__exam=exam
    ).select_related(
        "stdexam__student",
        "stdexam__exam"
    )

    if not results.exists():
        messages.error(request, "No results are available to publish.")
        return redirect("Teacher:ExamResults")

    published_count = 0
    email_failures = 0

    # Publish the results
    with transaction.atomic():
        for result in results:
            result.published = True
            result.published_date = timezone.now()
            result.save(update_fields=["published", "published_date"])

    # Locate the ScriptVision logo
    logo_path = finders.find("Main/img/scriptvisionlogo.png")

    # Send result notification emails
    for result in results:

        student = result.stdexam.student

        if not student.student_email:
            email_failures += 1
            continue

        subject = f"ScriptVision - Results Published: {exam.exam_name}"

        marks = (
            str(result.total_final_marks)
            if result.total_final_marks is not None
            else "Not available"
        )

        # Plain-text fallback
        text_content = (
            f"Dear {student.student_name},\n\n"
            "The results for your examination have been published.\n\n"
            f"Exam: {exam.exam_name}\n"
            f"Subject: {exam.subject.subject_name}\n"
            f"Marks: {marks} / {exam.total_marks}\n\n"
            "Please log in to ScriptVision to view your complete result "
            "and evaluation feedback.\n\n"
            "Regards,\n"
            "ScriptVision Team"
        )

        # HTML email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f3f4f8;
                     font-family:Arial,Helvetica,sans-serif;color:#25243a;">

        <table role="presentation" width="100%" cellspacing="0"
               cellpadding="0" style="padding:30px 12px;">
        <tr>
        <td align="center">

        <table role="presentation" width="600" cellspacing="0"
               cellpadding="0" style="max-width:600px;width:100%;
               background:#ffffff;border-radius:14px;overflow:hidden;">

            <tr>
                <td style="background:#11111a;padding:24px 30px;color:#ffffff;">
                    <table role="presentation" cellspacing="0" cellpadding="0">
                    <tr>
                        <td style="vertical-align:middle;padding-right:12px;">
                            <img src="cid:scriptvision_logo"
                                 alt="ScriptVision" width="48" height="48"
                                 style="display:block;object-fit:contain;">
                        </td>
                        <td style="vertical-align:middle;">
                            <div style="font-size:23px;font-weight:bold;">
                                ScriptVision
                            </div>
                            <div style="font-size:12px;color:#b7b7c5;margin-top:5px;">
                                AI-Based Handwritten Answer Evaluation
                            </div>
                        </td>
                    </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td style="padding:32px 30px;">

                    <div style="font-size:12px;font-weight:bold;
                                letter-spacing:2px;color:#8055e8;">
                        EXAMINATION UPDATE
                    </div>

                    <h1 style="font-size:25px;line-height:1.3;
                               margin:14px 0;color:#202033;">
                        Results are published!
                    </h1>

                    <p style="font-size:15px;line-height:1.7;color:#55556a;">
                        Dear {student.student_name},
                    </p>

                    <p style="font-size:15px;line-height:1.7;color:#55556a;">
                        Your examination results are now available.
                        Here is your result summary.
                    </p>

                    <table role="presentation" width="100%" cellspacing="0"
                           cellpadding="0" style="background:#f5f2ff;
                           border:1px solid #e6ddff;border-radius:12px;">
                    <tr>
                        <td style="padding:22px;">

                            <div style="font-size:13px;color:#69647c;">
                                Examination
                            </div>

                            <div style="font-size:18px;font-weight:bold;
                                        margin:6px 0 16px;color:#242238;">
                                {exam.exam_name}
                            </div>

                            <div style="font-size:13px;color:#69647c;">
                                Subject
                            </div>

                            <div style="font-size:15px;font-weight:bold;
                                        margin:6px 0 18px;color:#242238;">
                                {exam.subject.subject_name}
                            </div>

                            <div style="font-size:13px;color:#69647c;">
                                Marks obtained
                            </div>

                            <div style="font-size:32px;font-weight:bold;
                                        color:#8055e8;margin-top:5px;">
                                {marks}
                                <span style="font-size:17px;color:#69647c;">
                                    / {exam.total_marks}
                                </span>
                            </div>

                        </td>
                    </tr>
                    </table>

                    <p style="font-size:14px;line-height:1.7;color:#55556a;
                              margin-top:24px;">
                        Log in to ScriptVision to view your complete result
                        and detailed evaluation feedback.
                    </p>

                    <p style="font-size:14px;line-height:1.7;color:#55556a;
                              margin-top:24px;">
                        Regards,<br>
                        <strong>ScriptVision Team</strong>
                    </p>

                </td>
            </tr>

            <tr>
                <td style="background:#11111a;padding:18px 25px;
                           text-align:center;color:#b7b7c5;font-size:12px;">
                    &copy; 2026 ScriptVision. All rights reserved.
                </td>
            </tr>

        </table>
        </td>
        </tr>
        </table>

        </body>
        </html>
        """

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[student.student_email]
            )

            email.attach_alternative(html_content, "text/html")

            # Attach the actual logo inline
            if logo_path:
                with open(logo_path, "rb") as logo_file:
                    logo = MIMEImage(logo_file.read())
                    logo.add_header(
                        "Content-ID",
                        "<scriptvision_logo>"
                    )
                    logo.add_header(
                        "Content-Disposition",
                        "inline",
                        filename="scriptvisionlogo.png"
                    )
                    email.attach(logo)

            email.send(fail_silently=False)
            published_count += 1

        except Exception as e:
            email_failures += 1
            print(
                f"Email failed for student "
                f"{student.student_id}: {e}"
            )

    # Display status
    if email_failures:
        messages.warning(
            request,
            f"Results published. {published_count} email(s) sent; "
            f"{email_failures} email(s) could not be sent."
        )
    else:
        messages.success(
            request,
            f"Results published successfully. "
            f"{published_count} notification email(s) sent."
        )

    return redirect("Teacher:ExamResults")