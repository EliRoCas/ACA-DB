# 👥 Guía de Configuración para Miembros del Equipo

## 📋 Instrucciones Paso a Paso

Sigue estos pasos exactos para configurar tu ambiente de desarrollo local.

### Paso 1: Clonar el Repositorio
```powershell
git clone <repository-url>
cd ACA-DB
```

### Paso 2: Crear Entorno Virtual
```powershell
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno
Copia el archivo de ejemplo:
```powershell
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### Paso 5: Generar tu Propia SECRET_KEY
**⚠️ IMPORTANTE: Cada persona debe generar su propia clave secreta**

Ejecuta este comando en tu terminal:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Verás un resultado como:
```
abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz
```

**COPIA ESTE RESULTADO**, lo necesitarás en el siguiente paso.

### Paso 6: Editar el Archivo `.env`
Abre el archivo `.env` que creaste en el paso 4 con tu editor de texto favorito.

**Busca esta línea:**
```env
SECRET_KEY=tu-nueva-secret-key-generada-aqui
```

**Y reemplázala con tu clave generada en el paso 5:**
```env
SECRET_KEY=abc123xyz789def456ghi789jkl012mno345pqr678stu901vwx234yz
DEBUG=True
```

**Guarda el archivo.**

### Paso 7: Ejecutar Migraciones
```powershell
python manage.py migrate
```

### Paso 8: Iniciar el Servidor
```powershell
python manage.py runserver
```

¡Listo! La aplicación estará disponible en: **http://127.0.0.1:8000/**

Abre tu navegador y verás la landing page de FitGym.

---

## 🔐 Reglas de Seguridad - MUY IMPORTANTE

| ✅ HACER | ❌ NO HACER |
|----------|-----------|
| Generar tu **propia** SECRET_KEY | Compartir tu SECRET_KEY con otros |
| Guardar `.env` **solo en tu máquina** | Commitear `.env` a Git |
| Usar `.env.example` como plantilla | Modificar `.env.example` con valores reales |
| Cada persona con su propia clave | Una clave compartida entre el equipo |

**Recuerda:** 
- El `.env` está protegido en `.gitignore` - nunca se subirá a GitHub automáticamente
- **NUNCA** compartas tu `.env` con compañeras
- Tu SECRET_KEY es personal y única

---

## 🆘 Solución de Problemas

### Problema: "No module named 'django'"
**Solución:**
```powershell
# Asegúrate de que el venv está activado
# Windows: .\venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate

# Luego instala las dependencias
pip install -r requirements.txt
```

### Problema: "No such table" al acceder a la web
**Solución:**
```powershell
python manage.py migrate
```

### Problema: VS Code no reconoce variables del `.env`
**Solución:**
1. Abre VS Code Settings: `Ctrl + ,`
2. Busca: `python.terminal.useEnvFile`
3. Marca el checkbox ✅

### Problema: Error "Port 8000 already in use"
**Solución:** Usa otro puerto:
```powershell
python manage.py runserver 8001
```

Luego accede a: **http://127.0.0.1:8001/**

### Problema: Error de Base de Datos
**Solución:**
```powershell
# Elimina el archivo db.sqlite3 y recrea la base de datos
rm db.sqlite3
python manage.py migrate
```

---

## 📤 Cómo Compartir Cambios con el Equipo

### Flujo Completo de Trabajo

```bash
# 1. Actualizar tu rama con los últimos cambios de main
git pull origin main

# 2. Crear rama para tu feature/bugfix
git checkout -b feature/nombre-descriptivo

# 3. Hacer cambios en los archivos

# 4. Ver cambios antes de commitear (MUY IMPORTANTE)
git status

# 5. Agregar cambios
git add .

# 6. VERIFICAR QUE .env NO APARECE EN LA LISTA
git status  # ← El .env NO debe aparecer aquí (protegido por .gitignore)

# 7. Commitear con mensaje descriptivo
git commit -m "feat: descripción clara del cambio"

# 8. Push a tu rama
git push origin feature/nombre-descriptivo

# 9. Crear Pull Request en GitHub para que revise el equipo

# 10. Después de que aprueben y hagan merge a main, actualizar tu rama local
git checkout main
git pull origin main

# 11. Limpiar rama local (opcional)
git branch -d feature/nombre-descriptivo
```

### Convenciones de Commits
Usa estos prefijos en tus mensajes:
- `feat:` - Nueva funcionalidad
- `fix:` - Bug fix
- `docs:` - Cambios en documentación
- `style:` - Cambios de código que no afectan lógica (espacios, formatos)
- `refactor:` - Refactorizar código sin cambiar funcionalidad
- `test:` - Agregar o modificar tests

**Ejemplos:**
```
feat: agregar validación de email en formulario
fix: arreglar error en página de login
docs: actualizar instrucciones de setup
```

---

## ✅ Checklist Antes de Commitear

Antes de hacer `git push`, verifica esto:

- [ ] `.env` NO aparece en `git status`
- [ ] Solo cambié archivos necesarios (sin `db.sqlite3`)
- [ ] El código está funcionando en `http://127.0.0.1:8000/`
- [ ] Mi SECRET_KEY es única (generada en mi máquina)
- [ ] El mensaje del commit es descriptivo y sigue convenciones
- [ ] No incluí dependencias externas sin actualizar `requirements.txt`
- [ ] No hay archivos `.pyc` o `__pycache__` (Git los ignora automáticamente)

---

## 📚 Recursos Útiles

- **Documentación de Django**: https://docs.djangoproject.com/
- **Documentación de Git**: https://git-scm.com/doc
- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **README del Proyecto**: Ver `README.md` en la raíz del repositorio

---

## 💬 Preguntas Frecuentes

**P: ¿Por qué cada uno genera su propia SECRET_KEY?**
R: Por seguridad. Si compartimos una clave, cualquiera que acceda al repositorio podría usarla. Cada máquina debe tener una clave única.

**P: ¿Qué pasa si accidentalmente commito mi `.env`?**
R: No te preocupes, está protegido por `.gitignore`. Aún así, si lo hiciste:
```bash
git rm --cached .env
git commit -m "remove .env from tracking"
git push
```

**P: ¿Mi SECRET_KEY se ve en git log?**
R: No, porque nunca se comitea. Solo existe en tu máquina local.

**P: ¿Necesito crear un nuevo .env cada vez que abro el proyecto?**
R: No, solo una vez. Guárdalo en tu máquina porque lo necesitarás cada vez que ejecutes el servidor.

**P: ¿Qué hago si se me olvida la SECRET_KEY?**
R: Simplemente genera una nueva ejecutando el comando de nuevo en el paso 5 y actualiza tu `.env`.

---

## ✋ Frente a Dudas

Si tienes dudas o problemas:
1. Revisa esta guía nuevamente
2. Abre un issue en GitHub con detalles del error

**¡Bienvenida al equipo FitGym!** 🎉
