# Forum Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

ARG INTERNAL_API_URL=http://backend:8000
ARG NEXT_PUBLIC_API_URL=
ENV INTERNAL_API_URL=${INTERNAL_API_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# 安装依赖
COPY package.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建
RUN npm run build

EXPOSE 3000

# 使用Node.js运行生产服务器
CMD ["node", "node_modules/next/dist/bin/next", "start", "-p", "3000"]
