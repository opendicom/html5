## OPENDICOM 
# Especialistas DICOMWEB™ y DICOM™

DICOMWEB™ es una extensión de DICOM™ para permitir la comunicación de imágenes médicas e informes por HTTP. Opendicom, nuestra compañia, se especializó en la arquitectura de sistemas que facilite esta comunicación hacia servicios en la nube y/o en forma distribuida.

Nuestros productos están diseñados para facilitar la interoperabilidad de soluciones DICOM™ pre existentes por complementación con extensiones DICOMWEB™. Son modulares y funcionalmente complementarios entre sí: cada nivel superior de funcionalidad requiere los niveles inferiores. Nuestra pila de aplicación consta con 5 niveles encima de la comunicación DICOM preexistente.

# Docker commands

- Iniciar y contruir contenedores: docker-compose up -d --build
- Iniciar contenedores: docker-compose up
- Detener contenedores: docker-compose stop
- Detener y remover contenedores: docker-compose down -v
- Ejecutar comand en contenedor django: docker-compose exec web "comando"
- Ver log: docker-compose logs -f 
 
