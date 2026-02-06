import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Django
from matplotlib import pyplot as plt

def results(churn_rate, churn_counts, feature_importances, accuracy):
    """Generate visualization and render results page"""
    # Plot churn distribution
    plt.figure(figsize=(8, 6))
    plt.pie(churn_counts.values, labels=['Not Churned', 'Churned'], autopct='%1.1f%%', startangle=90)
    plt.title('Customer Churn Distribution')

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    chart_base64 = base64.b64encode(image_png).decode('utf-8')

    context = {
        'churn_rate': churn_rate,
        'chart': chart_base64,
        'feature_importances': feature_importances.to_dict(),
        'accuracy': accuracy
    }
    
    return context