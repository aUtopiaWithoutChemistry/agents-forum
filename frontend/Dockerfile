# Forum Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# 安装依赖
COPY package.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建
RUN npm run build

EXPOSE 3000

# 使用Node.js运行生产服务器
CMD ["node", "node_modules/next/dist/bin-next", "start", "-p", "3000"]
