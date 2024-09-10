from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Tool
from .forms import ToolForm

@staff_member_required
def tool_settings(request):
    tools = Tool.objects.all()
    if request.method == 'POST':
        form = ToolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tool_settings')
    else:
        form = ToolForm()
    return render(request, 'tools/tool_settings.html', {'tools': tools, 'form': form})

@staff_member_required
def edit_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    if request.method == 'GET':
        data = {
            'name': tool.name,
            'icon': tool.icon,
            'description': tool.description,
            'is_featured': tool.is_featured,
        }
        return JsonResponse(data)
    elif request.method == 'POST':
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            updated_tool = form.save(commit=False)
            updated_tool.template_name = tool.template_name  # Keep the original template_name
            updated_tool.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})

@staff_member_required
def delete_tool(request, tool_id):
    tool = get_object_or_404(Tool, id=tool_id)
    if request.method == 'POST':
        tool.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def tool_view(request, tool_id):
    tool = Tool.objects.get(id=tool_id)
    return render(request, f'tools/{tool.template_name}.html', {'tool': tool})

def tools_page(request):
    featured_tools = Tool.objects.filter(is_featured=True)
    tools = Tool.objects.filter(is_featured=False)
    return render(request, 'tools/tools.html', {'featured_tools': featured_tools, 'tools': tools})

