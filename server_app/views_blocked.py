import win32com.client
import pythoncom
from django.shortcuts import render, redirect
from .models import Whitelist, Blacklist
from .forms import WhitelistForm, BlacklistForm

def update_gpo():
    pythoncom.CoInitialize()
    try:
        gpm = win32com.client.Dispatch("GPMgmt.GPM")
        gpo_guid = "FC6FB68D-5D14-4BC1-8BF0-43018F119787"  # Replace with your GPO GUID
        gpo = gpm.GetGPO(gpo_guid)
        gpo_section = gpo.GetSection(2)  # 2 for User Configuration

        gpo_section.DeleteAll()

        whitelist = Whitelist.objects.values_list('url', flat=True)
        blacklist = Blacklist.objects.values_list('url', flat=True)

        for url in whitelist:
            gpo_section.SetRegistryValue(
                "Software\\Policies\\Google\\Chrome\\URLWhitelist",
                url,
                "1",
                "REG_DWORD"
            )
            gpo_section.SetRegistryValue(
                "Software\\Policies\\Microsoft\\Edge\\URLAllowlist",
                url,
                "1",
                "REG_DWORD"
            )

        for url in blacklist:
            gpo_section.SetRegistryValue(
                "Software\\Policies\\Google\\Chrome\\URLBlacklist",
                url,
                "1",
                "REG_DWORD"
            )
            gpo_section.SetRegistryValue(
                "Software\\Policies\\Microsoft\\Edge\\URLBlocklist",
                url,
                "1",
                "REG_DWORD"
            )

        gpo_section.Save(True)
        print("GPO updated successfully with the latest whitelist and blacklist URLs.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pythoncom.CoUninitialize()

def manage_urls(request):
    if request.method == 'POST':
        if 'whitelist_url' in request.POST:
            whitelist_form = WhitelistForm(request.POST)
            if whitelist_form.is_valid():
                whitelist_form.save()
                update_gpo()
                return redirect('manage_urls')
        elif 'blacklist_url' in request.POST:
            blacklist_form = BlacklistForm(request.POST)
            if blacklist_form.is_valid():
                blacklist_form.save()
                update_gpo()
                return redirect('manage_urls')
    else:
        whitelist_form = WhitelistForm()
        blacklist_form = BlacklistForm()

    whitelisted_urls = Whitelist.objects.all()
    blacklisted_urls = Blacklist.objects.all()

    return render(request, 'server_app/manage_urls.html', {
        'whitelist_form': whitelist_form,
        'blacklist_form': blacklist_form,
        'whitelisted_urls': whitelisted_urls,
        'blacklisted_urls': blacklisted_urls,
    })

def remove_whitelist_url(request, url_id):
    url = Whitelist.objects.get(id=url_id)
    url.delete()
    update_gpo()
    return redirect('manage_urls')

def remove_blacklist_url(request, url_id):
    url = Blacklist.objects.get(id=url_id)
    url.delete()
    update_gpo()
    return redirect('manage_urls')
