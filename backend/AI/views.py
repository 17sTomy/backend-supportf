# emotion_analysis/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmotionAnalysisRequestSerializer, EmotionAnalysisResponseSerializer
from hume import HumeBatchClient
from hume.models.config import BurstConfig, ProsodyConfig
import time

class EmotionAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmotionAnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            client = HumeBatchClient("wTBNDAdijkElZeESa2GlJSGGpxNXdpAV1oqX2VrSa5cySmVA")
            burst_config = BurstConfig()
            prosody_config = ProsodyConfig()
            job = client.submit_job([url], [burst_config, prosody_config])
            job.await_complete()
            full_predictions = job.get_predictions()
            
            response_data = []
            for source in full_predictions:
                source_name = source["source"]["url"]
                predictions = source["results"]["predictions"]
                for prediction in predictions:
                    prosody_emotions = []
                    burst_emotions = []
                    
                    prosody_predictions = prediction["models"]["prosody"]["grouped_predictions"]
                    for prosody_prediction in prosody_predictions:
                        for segment in prosody_prediction["predictions"][:1]:
                            prosody_emotions.append(segment["emotions"])
                            
                    burst_predictions = prediction["models"]["burst"]["grouped_predictions"]
                    for burst_prediction in burst_predictions:
                        for segment in burst_prediction["predictions"][:1]:
                            burst_emotions.append(segment["emotions"])
                            
                    response_data.append({
                        "source_name": source_name,
                        "prosody_emotions": prosody_emotions,
                        "burst_emotions": burst_emotions
                    })

            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
