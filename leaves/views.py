from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.permissions import IsDoctor
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer, LeaveRequestCreateSerializer


class LeaveRequestListCreateView(APIView):
    """Doctor: list own leave requests or create a new one."""
    permission_classes = [IsDoctor]

    def get(self, request):
        leaves = LeaveRequest.objects.filter(doctor=request.user.doctor_profile)
        serializer = LeaveRequestSerializer(leaves, many=True)
        return Response({'success': True, 'data': serializer.data})

    def post(self, request):
        serializer = LeaveRequestCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            leave = serializer.save(doctor=request.user.doctor_profile)
            return Response({
                'success': True,
                'message': 'Leave request submitted successfully.',
                'data': LeaveRequestSerializer(leave).data,
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LeaveRequestDetailView(APIView):
    """Doctor: view or cancel a single leave request."""
    permission_classes = [IsDoctor]

    def get(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk, doctor=request.user.doctor_profile)
        return Response({'success': True, 'data': LeaveRequestSerializer(leave).data})

    def delete(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk, doctor=request.user.doctor_profile)
        if leave.status != LeaveRequest.Status.PENDING:
            return Response({
                'success': False,
                'message': 'Only pending leave requests can be cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        leave.delete()
        return Response({'success': True, 'message': 'Leave request cancelled.'})
