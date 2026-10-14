# Part A - Docker fundamentals (English study guide)

This original study guide supports the teacher's graded tutorial. The Drive
link in the assignment was not accessible during preparation. This document
does not claim to reproduce its content, answer unseen graded questions, or
prove completion of Part A. Follow the teacher's tutorial for the actual grade.

## 1. Images and containers

An image is a packaged filesystem plus runtime metadata. A container is a
running or stopped instance of an image, with its own writable layer. Containers
share the host kernel; Linux containers on Docker Desktop run inside its Linux
VM. They are not full virtual machines.

```sh
docker version
docker pull alpine:3.22
docker run --rm alpine:3.22 echo "Hello from Docker"
docker images
docker ps -a
```

`--rm` removes the container after exit. It does not remove the image.

## 2. Lifecycle and inspection

```sh
docker run -d --name practice alpine:3.22 sleep 600
docker logs practice
docker exec practice id
docker inspect practice
docker stop practice
docker start practice
docker rm -f practice
```

`docker exec` starts an additional process inside a running container. `stop`
sends the configured stop signal, usually SIGTERM, then kills the process after
the timeout. `rm -f` kills and removes a running container.

## 3. Build an application image

```sh
docker build -t counter-app:1.0 .
docker images counter-app:1.0
docker history counter-app:1.0
```

FROM selects the base; WORKDIR sets the working directory; COPY copies build
context files; RUN executes at build time; USER sets the runtime user; EXPOSE
documents a port; CMD defines the default startup command. Copy dependencies
first so changing application code does not reinstall them. A .dockerignore
keeps unnecessary files out of the build context. --no-cache-dir disables pip's
package-download cache, not Docker's build cache.

## 4. Networking

Containers on the user-defined bridge app-network can resolve each other by
name. The app uses db-service to reach Redis. localhost inside a container means
that container itself, not the Redis container or your laptop.

`-p 80:5000` maps host TCP port 80 to container TCP port 5000. Multiple containers
can all listen on their own port 5000, but cannot all bind the same host address
and port. EXPOSE alone does not publish a port.

## 5. Persistence

A container's writable layer is removed with the container. Named volumes have
an independent lifecycle. Mount redis-data at /data and enable Redis AOF so the
in-memory counter is written to the mounted storage. For the forced-removal TP,
appendfsync always prioritizes durability over throughput. Do not delete the
volume during the persistence test. Persistence is not a backup strategy.

## 6. Compose and scaling

```sh
docker compose config
docker compose up -d --build --scale web=3
docker compose ps
docker compose logs -f
docker compose down
```

Compose defines services, networks, volumes and environment variables. The web
service has no fixed container_name or host port mapping, so it can have three
replicas. A single Nginx load balancer publishes the host port and distributes
requests. depends_on with service_healthy waits for the declared health check;
it does not provide runtime high availability. One Redis and one load balancer
remain single points of failure in this educational architecture.

## 7. Registry and CI/CD

Tagging creates another image reference; it does not rebuild the image.
A registry stores image artifacts. Push requires the correct namespace and
credentials. Jenkins checks out main, installs dependencies, runs tests, builds
an image and pushes it only if preceding stages succeed. A webhook notifies
Jenkins after a Git push. Never store a registry token in Git or print it.

## Self-check with answers

1. **When do RUN and CMD execute?** RUN at build time; CMD at container startup.
2. **Why can't the app use localhost for Redis?** Redis runs in a different
   container network namespace; use the service name db-service.
3. **Is a volume enough to persist every visit?** No. Redis must also write its
   in-memory changes to files on that volume, for example through AOF.
4. **Why does scaling with 80:5000 fail?** Each replica attempts the same host
   binding. Publish only the load balancer or choose distinct host ports.
5. **Why run as non-root?** To limit privileges inside the container.
6. **Does docker compose down delete named volumes?** Not by default. --volumes
   removes the project's declared named volumes and attached anonymous volumes.
7. **Does docker system prune delete running containers?** No.
8. **What happens if unit tests fail?** The pipeline fails before image push.
9. **Why is INCR suitable for a shared counter?** Redis executes it atomically.
10. **Does a passing fake-Redis test prove disk persistence?** No. Test the real
    Redis container and volume with removal and recreation.

Official reference: https://docs.docker.com/get-started/
