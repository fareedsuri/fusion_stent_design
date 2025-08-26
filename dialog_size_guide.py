#!/usr/bin/env python3
"""
FUSION 360 DIALOG BOX SIZE CONTROL REFERENCE

This guide shows exactly where and how to control the startup width and height 
of your Fusion 360 dialog box.
"""


def print_dialog_size_controls():
    print("📐 FUSION 360 DIALOG BOX SIZE CONTROL GUIDE")
    print("=" * 60)

    print("\n📍 LOCATION IN CODE:")
    print("File: commands/commandDialog/entry.py")
    print("Function: command_created()")
    print("Line: ~208-220 (after input creation, before event handlers)")
    print("Look for: ⬅️ DIALOG BOX STARTUP WIDTH CONTROL")

    print("\n🎛️ DIALOG SIZE CONTROL METHODS:")
    print("=" * 50)

    print("\n1️⃣ setDialogInitialSize() - STARTUP SIZE:")
    print("   • Purpose: Sets the initial width and height when dialog opens")
    print("   • Usage: args.command.setDialogInitialSize(width, height)")
    print("   • Units: Pixels")
    print("   • Example: args.command.setDialogInitialSize(500, 600)")
    print("   • Effect: Dialog opens at 500px wide × 600px tall")

    print("\n2️⃣ setDialogMinimumSize() - MINIMUM SIZE:")
    print("   • Purpose: Prevents user from resizing dialog too small")
    print("   • Usage: args.command.setDialogMinimumSize(min_width, min_height)")
    print("   • Units: Pixels")
    print("   • Example: args.command.setDialogMinimumSize(400, 450)")
    print("   • Effect: User cannot make dialog smaller than 400×450")

    print("\n3️⃣ setDialogMaximumSize() - MAXIMUM SIZE:")
    print("   • Purpose: Prevents dialog from getting too large")
    print("   • Usage: args.command.setDialogMaximumSize(max_width, max_height)")
    print("   • Units: Pixels")
    print("   • Example: args.command.setDialogMaximumSize(800, 900)")
    print("   • Effect: User cannot make dialog larger than 800×900")

    print("\n📏 RECOMMENDED SIZES FOR YOUR STENT DESIGNER:")
    print("=" * 60)

    print("\n🎯 CURRENT SETTING:")
    print("   args.command.setDialogInitialSize(500, 600)")
    print("   args.command.setDialogMinimumSize(400, 450)")
    print("   Result: Opens at 500×600, minimum size 400×450")

    print("\n✨ ALTERNATIVE CONFIGURATIONS:")

    print("\n📱 Compact (for smaller screens):")
    print("   args.command.setDialogInitialSize(400, 500)")
    print("   args.command.setDialogMinimumSize(350, 400)")

    print("\n🖥️ Standard (good balance):")
    print("   args.command.setDialogInitialSize(500, 600)")
    print("   args.command.setDialogMinimumSize(400, 450)")

    print("\n🖥️ Wide (better for input visibility):")
    print("   args.command.setDialogInitialSize(600, 650)")
    print("   args.command.setDialogMinimumSize(500, 500)")

    print("\n🖥️ Large (for high-res displays):")
    print("   args.command.setDialogInitialSize(650, 750)")
    print("   args.command.setDialogMinimumSize(550, 600)")

    print("\n⚡ QUICK MODIFICATIONS:")
    print("=" * 50)

    print("\n🔧 To make dialog wider on startup:")
    print("Change line ~209 from:")
    print("   args.command.setDialogInitialSize(500, 600)")
    print("To:")
    print("   args.command.setDialogInitialSize(600, 600)  # Wider")
    print("   args.command.setDialogInitialSize(650, 650)  # Much wider")

    print("\n🔧 To make dialog taller on startup:")
    print("Change line ~209 from:")
    print("   args.command.setDialogInitialSize(500, 600)")
    print("To:")
    print("   args.command.setDialogInitialSize(500, 700)  # Taller")
    print("   args.command.setDialogInitialSize(500, 750)  # Much taller")

    print("\n🔧 To prevent dialog from being too small:")
    print("Adjust line ~212:")
    print("   args.command.setDialogMinimumSize(450, 500)  # Larger minimum")

    print("\n💡 TIPS FOR SIZING:")
    print("=" * 50)
    print("• Width 400-450: Compact, may feel cramped")
    print("• Width 500-550: Good balance for most screens")
    print("• Width 600-650: Spacious, good for input visibility")
    print("• Width 700+: Very wide, may not fit smaller screens")
    print()
    print("• Height 450-500: Compact, inputs may feel tight")
    print("• Height 550-650: Good balance")
    print("• Height 700+: Tall, good for many inputs")

    print("\n🎛️ TESTING SIZES:")
    print("=" * 50)
    print("1. Modify the size values in entry.py")
    print("2. Save the file")
    print("3. Restart the add-in in Fusion 360")
    print("4. Click the Stent Frame Designer button")
    print("5. Check if the dialog size looks good")
    print("6. Adjust and repeat until satisfied")


def print_exact_code_location():
    print("\n📝 EXACT CODE TO MODIFY:")
    print("=" * 50)
    print("File: commands/commandDialog/entry.py")
    print("Around line 209-220:")
    print()
    print("# ⬅️ DIALOG BOX STARTUP WIDTH CONTROL:")
    print("# Set the initial width and height of the dialog box")
    print("args.command.setDialogInitialSize(500, 600)  # ← CHANGE THESE VALUES")
    print()
    print("# Set minimum dialog size")
    print("args.command.setDialogMinimumSize(400, 450)  # ← CHANGE THESE VALUES")
    print()
    print("Example modifications:")
    print("args.command.setDialogInitialSize(600, 650)  # Wider and taller")
    print("args.command.setDialogMinimumSize(500, 500)  # Larger minimum")


if __name__ == "__main__":
    print_dialog_size_controls()
    print_exact_code_location()
