
"""
URL configuration for studybud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Health Check</title>
      <style>
        body {
          background: #f9fafb;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
          font-family: system-ui, sans-serif;
        }
        .status-box {
          background: white;
          border-radius: 1rem;
          box-shadow: 0 4px 10px rgba(0,0,0,0.1);
          padding: 2rem 3rem;
          text-align: center;
          border: 2px solid #4ade80;
        }
        .rocket {
          font-size: 3rem;
        }
        .title {
          font-size: 1.5rem;
          font-weight: 600;
          margin: 1rem 0;
          color: #374151;
        }
        .dot {
          height: 1rem;
          width: 1rem;
          background-color: #22c55e;
          border-radius: 50%;
          display: inline-block;
          animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.4); opacity: 0.6; }
          100% { transform: scale(1); opacity: 1; }
        }
      </style>
    </head>
    <body>
      <div class="status-box">
        <div class="rocket">🚀</div>
        <div class="title">Site up and running!</div>
        <div><span class="dot"></span> Live</div>
      </div>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('api/', include('base.api.urls')),
    path("healthz/", health, name="healthz")
]
