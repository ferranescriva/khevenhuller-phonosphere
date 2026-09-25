# Deployment · Despliegue

How to put this repository on GitHub, publish the page with GitHub Pages and mint a DOI through Zenodo.

Cómo subir este repositorio a GitHub, publicar la página con GitHub Pages y obtener un DOI a través de Zenodo.

---

## English

### 1. Create the repository

On GitHub, **New repository**. Suggested name `khevenhuller-phonosphere`. It must be **public** for the Zenodo integration to work. Do not add a README, a licence or a `.gitignore`, since this repository already has them.

### 2. Upload the files

Either drag the folder contents onto the empty repository page (**uploading an existing file**), or from a terminal:

```bash
cd khevenhuller-fonosfera
git init
git add .
git commit -m "Supplementary data and code for the Khevenhüller phonosphere article"
git branch -M main
git remote add origin https://github.com/USER/khevenhuller-phonosphere.git
git push -u origin main
```

### 3. Enable GitHub Pages

**Settings → Pages**. Under *Build and deployment*, set *Source* to **Deploy from a branch**, then branch `main` and folder `/ (root)`. Save. After a minute the page is live at `https://USER.github.io/khevenhuller-phonosphere/`, which serves `index.html` directly.

### 4. Connect Zenodo **before** releasing

Go to [zenodo.org](https://zenodo.org), sign in with GitHub, open **GitHub** in the account menu and switch the repository **on**. Zenodo only archives releases made *after* the switch is enabled, so this step comes before the next one.

### 5. Create a release

On GitHub, **Releases → Create a new release**. Tag `v1.0.0`, title `v1.0.0`, and a short description. Publish. Zenodo picks up the release within a few minutes, archives it and mints a DOI.

### 6. Record the DOI

Once Zenodo has issued it, add the DOI in three places:

- `README.md` and `README.es.md`, in the citation section
- `CITATION.cff`, adding `doi:` under the version
- the footer of `index.html`, replacing "DOI pending" (edit the string in `scripts/06_construir_web.py` and rebuild with `python3 scripts/06_construir_web.py`)

Zenodo also provides a *concept DOI* that always points to the latest version. That is the one to cite in the article.

---

## Español

### 1. Crear el repositorio

En GitHub, **New repository**. Nombre sugerido `khevenhuller-phonosphere`. Debe ser **público** para que funcione la integración con Zenodo. No añadas README, licencia ni `.gitignore`, porque este repositorio ya los trae.

### 2. Subir los ficheros

Arrastra el contenido de la carpeta sobre la página del repositorio vacío (**uploading an existing file**), o desde un terminal usa los comandos de la sección inglesa.

### 3. Activar GitHub Pages

**Settings → Pages**. En *Build and deployment*, elige *Source* → **Deploy from a branch**, rama `main` y carpeta `/ (root)`. Guarda. Al cabo de un minuto la página está en `https://USUARIO.github.io/khevenhuller-phonosphere/`.

### 4. Conectar Zenodo **antes** de publicar la release

Entra en [zenodo.org](https://zenodo.org), inicia sesión con GitHub, abre **GitHub** en el menú de la cuenta y activa el interruptor del repositorio. Zenodo solo archiva las releases posteriores a la activación, de modo que este paso va antes del siguiente.

### 5. Crear una release

En GitHub, **Releases → Create a new release**. Etiqueta `v1.0.0`, título `v1.0.0` y una descripción breve. Publica. Zenodo la recoge en unos minutos, la archiva y asigna el DOI.

### 6. Anotar el DOI

Cuando Zenodo lo emita, añádelo en tres sitios: la sección de cita de los dos README, el campo `doi:` de `CITATION.cff`, y el pie de `index.html`, sustituyendo «DOI pendiente de asignación» en `scripts/06_construir_web.py` y regenerando la página.

Zenodo entrega además un *concept DOI* que apunta siempre a la última versión. Ese es el que conviene citar en el artículo.

---

## Notes · Notas

The `corpus/` folder stays empty on purpose and `.gitignore` excludes its contents, because the source editions are under copyright.

La carpeta `corpus/` queda vacía a propósito y `.gitignore` excluye su contenido, porque las ediciones fuente están sujetas a derechos de autor.
