from server_app.models import Computer

def change_computer_name(computer_name, mac_address):
    name_mac_match = Computer.objects.filter(computer_name = computer_name, mac_address = mac_address).first()
    mac_found = Computer.objects.filter(mac_address = mac_address).first()
    computer = " "

    if not name_mac_match: 
        if mac_found: 
            mac_found.computer_name = computer_name
            mac_found.save()
            computer = mac_found
        else :

            newComputer = Computer(
                computer_name = computer_name, 
                mac_address = mac_address, 
            )

            if newComputer: 
                newComputer.save()
                computer = Computer.objects.filter(computer_name = computer_name).first()

    else : 
        computer = name_mac_match

    return computer