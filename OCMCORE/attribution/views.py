from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.http import HttpResponse
from core.services import (
    generate_attribution_service, 
    generate_attribution_excel
)
from rest_framework.decorators import api_view
import pandas as pd
from datetime import datetime
import json
from django.shortcuts import render

class GenerateAttributionInputSerializer(serializers.Serializer):
    beg_date = serializers.DateField()
    end_date = serializers.DateField()
    id1 = serializers.IntegerField()
    id2 = serializers.IntegerField()
    attributes = serializers.ListField(child=serializers.CharField())

class GenerateAttribution(APIView):
    """
    Endpoint that accepts beg_date, end_date, id1, id2, and a list of attributes for attribution generation.
    Calls a stored procedure and returns the results as JSON or Excel.
    """
    def post(self, request):
        serializer = GenerateAttributionInputSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if request.query_params.get('format') == 'excel':
                output, filename = generate_attribution_excel(
                    data['beg_date'],
                    data['end_date'],
                    data['id1'],
                    data['id2'],
                    data['attributes']
                )
                response = HttpResponse(
                    output.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                results = generate_attribution_service(
                    data['beg_date'],
                    data['end_date'],
                    data['id1'],
                    data['id2'],
                    data['attributes']
                )
                return Response({'results': results}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def generate_attribution(request):
    """
    Generate attribution data based on input parameters.
    
    Expected JSON payload:
    {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31", 
        "id1": "value1",
        "id2": "value2",
        "attributes": ["attr1", "attr2", "attr3"]
    }
    """
    try:
        # Extract parameters from request
        data = request.data
        
        # Validate required fields
        required_fields = ['start_date', 'end_date', 'id1', 'id2', 'attributes']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        start_date = data['start_date']
        end_date = data['end_date']
        id1 = data['id1']
        id2 = data['id2']
        attributes = data['attributes']
        
        # Validate dates
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate attributes is a list
        if not isinstance(attributes, list) or len(attributes) == 0:
            return Response(
                {'error': 'Attributes must be a non-empty list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Call the attribution service to generate data
        from attribution.services import generate_attribution_data
        
        result_df = generate_attribution_data(
            start_date=start_date,
            end_date=end_date,
            id1=id1,
            id2=id2,
            attributes=attributes
        )
        
        # Convert DataFrame to JSON-serializable format
        if result_df is not None and not result_df.empty:
            # Convert DataFrame to records (list of dictionaries)
            records = result_df.to_dict('records')
            
            # Get column names for frontend
            columns = list(result_df.columns)
            
            return Response({
                'success': True,
                'data': records,
                'columns': columns,
                'total_rows': len(records),
                'start_date': start_date,
                'end_date': end_date,
                'id1': id1,
                'id2': id2,
                'attributes': attributes
            })
        else:
            return Response({
                'success': True,
                'data': [],
                'columns': [],
                'total_rows': 0,
                'message': 'No data found for the specified criteria'
            })
            
    except Exception as e:
        return Response(
            {'error': f'Failed to generate attribution data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_attribution_config(request):
    """
    Get configuration for attribution form (available IDs and attributes).
    """
    try:
        # This would typically come from your database or configuration
        # For now, providing sample configuration
        config = {
            'available_ids': [
                {'name': 'customer_id', 'label': 'Customer ID', 'type': 'text'},
                {'name': 'order_id', 'label': 'Order ID', 'type': 'text'},
                {'name': 'product_id', 'label': 'Product ID', 'type': 'text'},
                {'name': 'user_id', 'label': 'User ID', 'type': 'text'},
                {'name': 'session_id', 'label': 'Session ID', 'type': 'text'}
            ],
            'available_attributes': [
                {'name': 'revenue', 'label': 'Revenue', 'type': 'numeric'},
                {'name': 'conversions', 'label': 'Conversions', 'type': 'numeric'},
                {'name': 'clicks', 'label': 'Clicks', 'type': 'numeric'},
                {'name': 'impressions', 'label': 'Impressions', 'type': 'numeric'},
                {'name': 'campaign_name', 'label': 'Campaign Name', 'type': 'text'},
                {'name': 'channel', 'label': 'Channel', 'type': 'text'},
                {'name': 'device_type', 'label': 'Device Type', 'type': 'text'},
                {'name': 'geo_location', 'label': 'Geographic Location', 'type': 'text'},
                {'name': 'time_of_day', 'label': 'Time of Day', 'type': 'text'},
                {'name': 'day_of_week', 'label': 'Day of Week', 'type': 'text'}
            ],
            'max_attributes': 10,
            'min_attributes': 1
        }
        
        return Response(config)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get configuration: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class AttributionAnalyzerView(APIView):
    """
    Web interface view for attribution analysis.
    """
    
    def get(self, request):
        """Render the attribution analyzer web interface."""
        return render(request, 'attribution/attribution_analyzer.html')

@api_view(['POST'])
def analyze_securities(request):
    """
    Analyze securities data using existing attribution API and create graphs.
    
    Expected JSON payload:
    {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "id1": "portfolio_id",
        "id2": "benchmark_id",
        "analysis_levels": ["daily", "aggregate"],
        "chart_types": ["line", "bar", "pie", "heatmap", "scatter"]
    }
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['start_date', 'end_date', 'id1', 'id2']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        start_date = data['start_date']
        end_date = data['end_date']
        id1 = data['id1']
        id2 = data['id2']
        analysis_levels = data.get('analysis_levels', ['daily', 'aggregate'])
        chart_types = data.get('chart_types', ['line', 'bar', 'pie', 'heatmap', 'scatter'])
        
        # Validate dates
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Call the existing attribution service to get DataFrame
        from attribution.services import generate_attribution_data, create_securities_charts
        
        # Get attribution data using existing API
        df = generate_attribution_data(
            start_date=start_date,
            end_date=end_date,
            id1=id1,
            id2=id2,
            attributes=['*']  # Get all attributes
        )
        
        if df.empty:
            return Response(
                {'error': 'No data found for the specified parameters'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create charts based on the DataFrame
        charts_data = create_securities_charts(
            df=df,
            analysis_levels=analysis_levels,
            chart_types=chart_types
        )
        
        # Prepare response
        results = {
            'summary': {
                'date_range': f"{start_date} to {end_date}",
                'id1': id1,
                'id2': id2,
                'total_records': len(df),
                'columns': list(df.columns),
                'data_preview': df.head(5).to_dict('records')
            },
            'charts': charts_data
        }
        
        return Response(results)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to analyze securities: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_securities_config(request):
    """
    Get configuration for securities analysis.
    """
    try:
        config = {
            'analysis_levels': [
                {'name': 'daily', 'label': 'Daily Level', 'description': 'Day-by-day analysis'},
                {'name': 'aggregate', 'label': 'Aggregate Level', 'description': 'Summary over date range'}
            ],
            'chart_types': [
                {'name': 'line', 'label': 'Line Chart', 'description': 'Show trends over time'},
                {'name': 'bar', 'label': 'Bar Chart', 'description': 'Compare values across categories'},
                {'name': 'pie', 'label': 'Pie Chart', 'description': 'Show proportions'},
                {'name': 'heatmap', 'label': 'Heatmap', 'description': 'Show correlation matrix'},
                {'name': 'scatter', 'label': 'Scatter Plot', 'description': 'Show relationships between variables'}
            ],
            'sample_ids': [
                'portfolio_001', 'portfolio_002', 'portfolio_003',
                'benchmark_001', 'benchmark_002', 'benchmark_003'
            ],
            'api_structure': {
                'required_fields': ['start_date', 'end_date', 'id1', 'id2'],
                'optional_fields': ['analysis_levels', 'chart_types'],
                'description': 'Uses existing generate_attribution_data API to fetch data and create charts'
            }
        }
        
        return Response(config)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get configuration: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class SecuritiesAnalyzerView(APIView):
    """
    Web interface view for securities analysis and graphing.
    """
    
    def get(self, request):
        """Render the securities analyzer web interface."""
        return render(request, 'attribution/securities_analyzer.html') 