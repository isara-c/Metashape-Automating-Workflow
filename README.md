# Metashape-Automating-Workflow

## Require

Metashape Pro

```sh
Metashape Pro version 1.6.0 +
```

## Option

Include 3 option in 1 scripts

```sh

1. Alignment + Reconstruction
2. Alignment + Reconstruction + Build all --> With GCPs
3. Alignment + Reconstruction + Build all --> No GCPs
```

## Usage

- Import your photo 
- Run script Metashape-Automating-Workflow.py after that select CRS as same type's GCPs
- After Align and reconstruction, script will ask you about GCPs and option to build
- Script will add FixGCP and BuildAll to menu toolbar if you have GCP 


## FixGCP 

After adjust your GCPs, this menu help you to get more accuracy because this menu will filter picture have error more than value that you input
- Input maximum error you want to accept
- Program will show pictures have error more than value that you input on Photo tab
- Run FixGCP until program show accept

## BuildAll 

Program will build Orthophoto and DSM 

## Meta

Isara Chaowuttisuk – chaowuttisuk@hotmail.com

## Credit

Assoc. Prof. Vichai Yiengveerachon

Thirawat Bannakulpiphat

Agisoft Community ( https://www.agisoft.com/forum/index.php?board=17.0 )

