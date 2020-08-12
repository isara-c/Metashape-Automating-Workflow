# Metashape-Automating-Workflow
 
** metashape version 1.6.0 +

Script for automating workflow

Include 3 option in 1 scripts
1. Alignment + Reconstruction
2. Alignment + Reconstruction + Build all --> With GCPs
3. Alignment + Reconstruction + Build all --> No GCPs

Main step

- Import your photo 
- Run script Metashape-Automating-Workflow.py after that select CRS as same type's GCPs
- After Align and reconstruction, script will ask you about GCPs and option to build
- Script will add FixGCP and BuildAll to menu toolbar if you have GCP 

FixGCP 

After adjust your GCPs, this menu help you to get more accuracy because this menu will filter picture have error more than value that you input
- Input maximum error you want to accept
- Program will show pictures have error more than value that you input on Photo tab
- Run FixGCP until program show accept

Isara Chaowuttisuk
Senior student
Department of Survey Engineering
School of Engineering
Chulalongkoen University
