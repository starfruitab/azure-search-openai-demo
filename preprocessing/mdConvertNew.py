import markdownify

# Example HTML to convert to Markdown
html_text = '<!-- The list below explains the different parts of the illustration. --><ol class="poslist" start="1"><div class="poscol"><li id="EmergencyStopWireEmergencyStopWires-62A17608" value="1">Emergency stop wire</li></div></ol></div><!-- The image below is used to illustrate the steps in the procedure (explained above in text) --><div><img alt="Illustration" class="illustration" loading="lazy" src="https://stsp3lqew6l65ci.blob.core.windows.net/illustrations/0000135640.png"/><strong>Valid for:</strong> Other countiesThe illustration shows the <b title="None">XH</b> with <b title="None">IC</b> variant.</div><!-- The image below is used to illustrate the steps in the procedure (explained above in text) --><div><img alt="Illustration" class="illustration" loading="lazy" src="https://stsp3lqew6l65ci.blob.core.windows.net/illustrations/0000401736.png"/><strong>Valid for:</strong> USA and CanadaThe illustration shows the <b title="None">XH</b> with <b title="None">IC</b> variant.</div></section><!-- Start of section about Safeguards --><section class="section" id="section151"><h3>Safeguards</h3><div class="safetymessage">Moving machinery parts.Never defeat or bypass the interlocking devices.</div>Movable guards, for example, doors and covers leading to hazardous zones, are fitted with interlocking devices where required. These devices are usually electric safety switches that are parts of the safety system and must never be defeated, bypassed, or otherwise made inoperative.Where movable guards (doors) are equipped with means to be locked in a nonclosed position, any person with the intention to preside, for any reason, behind such a guard must lock the guard in the nonclosed position by use of a padlock.<strong>Note:</strong> For work on the electrical equipment, the electrical power must also be disconnected.<div class="safetymessage">Equipment damage.The equipment can be damaged if it is not stopped in the correct way. Never stop this equipment by opening a movable guard, for example, a door or cover, equipped with an interlocking device.</div>The location of each interlocking device is shown by an arrow.<!-- The image below is used to illustrate the steps in the procedure (explained above in text) --><div>'

# Convert HTML to Markdown using markdownify
markdown_text_alternative = markdownify.markdownify(html_text, heading_style="ATX")


print(markdown_text_alternative)


# Import markdownify module

# Create complex HTML text to be converted
html_text = """
<!-- The list below explains the different parts of the illustration. -->
<div class="article">
   <h1>My HTML Title</h1>
   <p>This is some sample HTML text.</p>
   <ul>
      <li>Item 1</li>
      <li>Item 2</li>
      <li>Item 3</li>
   </ul>
   <a href="https://www.tutorialspoint.com">Link to TutorialsPoint</a>
</div>
"""
# Use markdownify() function to convert HTML to Markdown
markdown_text = markdownify.markdownify(html_text, heading_style="ATX")

# Display the converted Markdown text
print(markdown_text)