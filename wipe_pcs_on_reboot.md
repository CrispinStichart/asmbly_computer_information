
# Comparison of methods and software for wiping changes from shared computer

(skip to the end for my recommendation)

This write-up is an analysis of different the different methods and software available to restore a Windows computer to a clean state. The reason we would want this to reduce the risk of anyone accidentally or purposefully breaking Windows, installing unwanted software, or leaving personal information on the computer (like in a browser session). 

Since we don't want to limit the computer's functionality, the solutions employed for some public PCs, like at a library, won't work. Library computers will often be extremely locked down, with only a browser accessible. This is done using a custom shell or [kiosk mode](https://learn.microsoft.com/en-us/windows/configuration/kiosk-single-app). However, we just want any change to persist only until the next logout or reboot.  

The three primary ways of doing this are full virtualization, file system virtualization, and disk imaging/restoring.


## Full virtualization

Full virtualization would involve running another instance of Windows in a virtual machine. This would be done via applications like VirtualBox or VMWare, or (in recent versions of Windows) Windows Sandbox. 

Although this does ensure full separation from the host computer, the primary downsides are:

1) Since these virtual machines run in a window, the only officially supported way to lock the window open and render other parts of the host inaccessible would be to use Kiosk Mode, which is only available in Windows Pro and above editions. 
2) Lag. There's no GPU acceleration, so even dragging a window around is choppy -- you can forget about comfortably using a 3d program like PrusaSlicer, and even a 2d tool like LightBurn or Corral would probably be affected.


## File System Virtualization

With this method, we redirect all writes to a virtual overlay that's stored in memory. This can be accomplished through the built-in [Unified Write Filter](https://learn.microsoft.com/en-us/windows-hardware/customize/enterprise/unified-write-filter) (UWF). A beneficial side effect of this method is that file IO become extremely fast, since it's all in memory. In addition, the lifespan of SSDs will be extended.

The hangup with enabling UWF directly is that it's only officially supported on Enterprise and Education editions. Pro [may work](https://superuser.com/questions/956282/is-unified-write-filter-part-of-windows-10-pro), but I haven't had a chance to test it. Luckily, there are third party tools that do the same thing (and, I'm guessing, are built on top of UWF) but support more Windows versions. 

Toolwiz Time Freeze is one such application, and is the only free third-party offering I could find. It provides a system tray icon and simple GUI to disable/enable the overlay. In addition, it can be [controlled from the command line](https://www.neowin.net/news/toolwiz-time-freeze-2203200/), which is important for automating updates.

Running Time Freeze does reduce the available RAM, since you need to allocate the size of the virtual file system up front, but you still need to leave some for Windows. Of the five main computers (the four lasers and one common room) Dorian has 12 gigs of RAM and the rest have 16. Microsoft [suggests 2 gigs](https://www.microsoft.com/en-us/windows/windows-10-specifications) are all that's needed for Windows 10 (64-bit), which would give us 10 gigs on Dorian and 14 on the rest, which seems like enough when coupled with a nightly reboot.

## Backup/Restoring

The last strategy is to back up the drive once, and then restore that backup when you boot, wiping any changes that have been made in the interim. There are many tools to create backups, including Windows' built in tools, but the sticking point for us is that we want to restore the backup every time we reboot. The only free software I've found that does this is the freeware [Reboot Restore Rx](https://horizondatasys.com/reboot-restore-rx-freeware/).  

I tested it, and it works as advertised. The restore process is very quick. Its main limitation is that the free version doesn't allow update scheduling, and as far as I can tell doesn't let you control it from the command line. If you want to apply Windows Updates, you have to disable it manually and run the updater.

# The Way Forward

My recommendation is to user Toolwiz Time Freeze. It's free, and at some later point, we can set up a script that will automatically disable it and run updates overnight.

The only immediate configuration change we would want to make is to [schedule a reboot](https://v2cloud.com/tutorials/how-to-configure-windows-to-reboot-automatically-on-schedule) every night, so the virtual file system doesn't fill up. 

In addition, before enabling it, we would want to tidy up -- clear up the Downloads folder, wipe chrome profiles, etc. The quickest way to do that would probably be to create a new user account. 

## Computer Checklist

1. [schedule a nightly reboot](https://v2cloud.com/tutorials/how-to-configure-windows-to-reboot-automatically-on-schedule) at 4:00 AM
2. create a new user
	* non-admin user
	* set to log in automatically without password
3. install [Toolwiz Time Freeze](https://www.toolwiz.com/lead/toolwiz_time_freeze/) (scroll down for the download button)
	* check the "enable" box after installation, or enable from the system tray icon
4. reboot
5. enjoy

## Trial Run

I suggest doing a trial run on the common room PC. That way if something goes super wrong, at least it's not blocking a laser. 
