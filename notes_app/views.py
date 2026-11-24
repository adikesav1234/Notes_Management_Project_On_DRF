from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth.models import User
from notes_app.models import NotesDB,TokenDb
from notes_app.serializers import RegisterSerializer,NoteSerializer,serializers,TokenSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
class RegisterView(APIView):
    def post(self,request):
        serializer_instance=RegisterSerializer(data=request.data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response({"Message":"Registration Successfull...!"})
        else:
            return Response(serializer_instance.errors)

class NoteListCreateView(APIView):

    permission_classes=[IsAuthenticated]

    def get(self,request):
        notes=NotesDB.objects.filter(user=request.user)
        serializer_instance=NoteSerializer(notes,many=True)
        return Response(serializer_instance.data)
    def post(self,request):
        serializer_instance=NoteSerializer(data=request.data)
        if serializer_instance.is_valid():
            serializer_instance.save(user=request.user)
            #because we only provide title and description,to provide user and created at also...we provide request.user to get the details of the user requesting   
            return Response(data=serializer_instance.data)
        else:
            return Response (data=serializer_instance.errors )

class NotesRetrieveUpdateDelete(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,request,pk):
        notes_id=get_object_or_404(NotesDB,id=pk)
        serializer_instance=NoteSerializer(notes_id)
        if notes_id.user != request.user:
            raise serializers.ValidationError('You dont have access to this')
        return Response(data=serializer_instance.data)
    
    def put(self,request,pk):
        request_body=request.data
        notes=get_object_or_404(NotesDB,id=pk)
        if notes.user!=request.user:
            raise serializers.ValidationError("You cant access this...!")
        serializer_instance=NoteSerializer(data=request_body,instance=notes)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

    def delete(self,request,pk):
        Note_id=get_object_or_404(NotesDB,id=pk)
        if Note_id.user != request.user :
            raise serializers.ValidationError("You cant access this...! ")
        Note_id.delete()
        return Response({"Message":"Note Has Been deleted...!"})

class TokenListCreateView(APIView):

    permission_classes=[IsAuthenticated]

    def get(self,request):
        tasks=TokenDb.objects.filter(user=request.user)
        serializer_instance=TokenSerializer(tasks,many=True)
        return Response(serializer_instance.data)
    
    def post(self,request):
        serializer_instance=TokenSerializer(data=request.data)
        if serializer_instance.is_valid():
            serializer_instance.save(user=request.user)
            return Response(data=serializer_instance.data)
        else:
            return Response (data=serializer_instance.errors )            

class TokenRetrieveDeleteUpdateView(APIView):
    permission_class = [IsAuthenticated]

    def get_token(self,request,id):
        return get_object_or_404(TokenDb,id=id,user=request.user)
    
    #READ SINGLE TASK
    def get(self,request,id):
        token=self.get_token(request,id)
        serializer_instance=TokenSerializer(token)
        return Response(serializer_instance.data)

    def put(self,request,id):
        token=self.get_token(request,id)
        serializer_instance=TokenSerializer(token,data=request.data)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(serializer_instance.data)
        return Response(serializer_instance.errors)

    def delete(self,request,id):
        token=self.get_token(request,id)
        token.delete()
        return Response({
            "Message":"Task deleted Successfully...!"
        })


class JWT_Logout(APIView):
    def post(self,request):
        try:
            refresh_token = request.data.get('refresh')
            token=RefreshToken(refresh_token)
            token.blacklist
            return Response({
                "Message":"Logout Success...!"
            })
        
        except Exception:
            return Response({
                "Error":'Invalid refresh token...!'
            })

        
