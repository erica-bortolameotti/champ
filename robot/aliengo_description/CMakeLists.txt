cmake_minimum_required(VERSION 3.5)
project(aliengo_description)

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

# Crea la directory lib/project_name anche se è vuota per evitare errori di libexec
install(DIRECTORY DESTINATION lib/${PROJECT_NAME})

# Installa le directory delle risorse
install(
  DIRECTORY 
    xacro
    meshes
    urdf
    rviz
    config
    launch    
  DESTINATION share/${PROJECT_NAME}
)

ament_package()