# Computer Information Collection
`get_info.ps1` is a PowerShell script that will collect information about the computer and save it a JSON file. As of now (10/23/22) the JSON files present in this repo don't match exactly with what the script produces, since I made some simplifications to the script after the data collection. 

Currently, the bulk of the information comes from the PowerShell built-in `Get-ComputerInfo`. A notable missing piece is the registration status of Windows; I thought the `OsStatus` field was the registration status, but I was wrong.

The script also collects a list of installed programs, for which I adapted [this script](https://devblogs.microsoft.com/scripting/use-powershell-to-quickly-find-installed-software/). I'm realizing as I write this that the list isn't complete; Google Chrome is an obvious omission. I'll look into why that is and if I need to combine strategies to get a more complete list.  

I ran this on all four laser-room PCs, as well as the PC to the left of the Mac. I didn't check the Mac yet (I'll put together a shell script for that later). The PC on the right was having problems when I was there; the mouse wasn't working, and keyboard navigation got me as far as running the script, but there was an error of some kind and I didn't bother trying to debug it. 

`parse_json.py` contains code that parses the JSON and creates Markdown tables. For the specs displayed below, I'm pulling what I think is the most relevant information, but there's plenty more stuff in the JSON. 

The list of installed programs can be found in [output/installed_software.md](output/installed_software.md), grouped by PC. This list is filtered to remove cruft like C++ Redistributables and graphics drivers. There's also a CSV file with the full list, so you can load it into SQLite and do SQL queries, if you want to know something like "what's the list of software that the laser room PCs have in common". 

## Specs


| Location | OS | RAM | CPU | User Name | Registered User | IP |
|  --- |  --- |  --- |  --- |  --- |  --- |  --- | 
| Laser Blue | Microsoft Windows 10 Pro | 16.8 GB | 3.4 MHz | DESKTOP-0HAB9M8\LaserHacker | admin@atxhs.org | 192.168.0.36 |
| Laser Dorian | Microsoft Windows 10 Pro | 12.6 GB | 3.2 MHz | DESKTOP-9K0E6DG\Dorian Grey | Dorian Grey | 192.168.0.196 |
| Laser Pearl | Microsoft Windows 10 Home | 16.8 GB | 3.3 MHz | DESKTOP-N3EN4LC\atxhacker | atxhsadmin@gmail.com | 192.168.0.42 |
| Laser Tarkin | Microsoft Windows 10 Home | 16.8 GB | 3.2 MHz | DESKTOP-6TEVT54\TarkinUser | admin@atxhs.org | 192.168.0.104 |
| Left Common Room | Microsoft Windows 10 Pro | 16.8 GB | 3.6 MHz | DESKTOP-DAJBCRD\Red Laser User | ATXHS Red Laser PC | 192.168.0.27 |


# Some Other Thoughts
## Admin Accounts
I noticed that only some of the user accounts were locked down, while others are admin accounts. It would *probably* be a good idea to lock them all down; whenever I see a bunch of shared computers with admin access, I always think about a childhood friend who installed keyloggers on all the library computers. 

Of course, you can still do malicious things with a shared non-admin account, and these days you can easily buy hardware keyloggers anyway. And besides all that, everyone has two-factor authentication enabled for everything that matters.... hopefully. So although seeing shared computers with admin access gives me a not-so-great feeling, it's probably not that big of a deal.    

## Remote Administration
Even with a small number of PCs, it'd be nice to be able to remotely administer them. And I don't even mean "remote" as in from outside the building -- there's still a lot of value in being able to do the same thing to every computer without walking around to all of them. Install updates, run scripts like the above to see software changes, install software simultaneously on all of them, and uh... other stuff?

Anyway, PowerShell has support for remoting into machines. Essentially its version of SSH. It [looks simple enough](https://learn.microsoft.com/en-us/powershell/scripting/learn/remoting/powershell-remoting-faq?view=powershell-7.2), but I haven't actually tried much with it. 

## User Management
The concept here is that instead of having one shared account, each user would have their own account that they could log into from any computer, and they could access their personal files. 

In addition to the convince of being able to have settings and files persist and be accessible from anywhere, this would also improve privacy and security. I'm sure that right now, people frequently log in to a website and forget to log out, which wouldn't be an issue with separate user accounts. 

Dovetailing with the previous suggestion to lock down admin accounts, having separate user accounts is probably the only way of truly preventing malicious actions (at least on the software side).

Obviously, this requires user information to be stored on a server, and for Windows, that means using [Active Directory](https://en.wikipedia.org/wiki/Active_Directory) That requires licensing Windows Server, which would get really expensive, because you need to purchase not only a server license (which, weirdly enough, is on a [per-core basis](https://www.microsoft.com/en-us/licensing/product-licensing/windows-server)) but also licenses for each user. 

From what I understand, the open-source [Samba](https://en.wikipedia.org/wiki/Samba_(software)) can replace Active Directory, and there's a [Linux Distro](https://en.wikipedia.org/wiki/Univention_Corporate_Server) that bundles Samba and a bunch of other useful things. However, in the end, the whole thing seems like a very complex task, that is probably not suited for a small nonprofit with no IT support on staff.
