# Switching Between Linux and Windows Containers

## Linux Containers (Recommended, SQL Authentication)
- Use: `Dockerfile.linux`, `docker-compose.linux.yml`, `env.linux`
- Start: `docker-compose -f docker-compose.linux.yml --env-file env.linux up -d`

## Windows Containers (Trusted Connection)
- Use: `Dockerfile.windows`, `docker-compose.windows.yml`, `env.windows`
- Start: `docker-compose -f docker-compose.windows.yml --env-file env.windows up -d`
- Make sure Docker is in Windows container mode (not Linux mode)

## Notes
- Linux containers are preferred for most deployments.
- Windows containers are only needed for trusted connection (Windows Authentication) to MSSQL.
- Nginx config and SSL setup are shared between both modes. 