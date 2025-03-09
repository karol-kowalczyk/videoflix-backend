from django.shortcuts import render

from django.core.mail import send_mail

class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"message": "E-Mail-Adresse erforderlich"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"message": "Kein Benutzer mit dieser E-Mail-Adresse gefunden"}, status=status.HTTP_404_NOT_FOUND)

        subject = 'Test'
        message = 'Testnachricht'
        from_email = 'test@example.com'
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            return Response({"message": "E-Mail gesendet."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Fehler beim Senden der E-Mail: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)