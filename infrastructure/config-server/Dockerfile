FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY config-server/pom.xml ./
RUN mvn dependency:go-offline
COPY config-server/src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/config-server-0.0.1-SNAPSHOT.jar app.jar
COPY config-repo /config-repo
EXPOSE 8888
ENTRYPOINT ["java", "-jar", "app.jar"]
