class WaveGradient {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        this.config = {
            waveAmplitude: 0.08,
            waveFrequency: 1.5,
            leftZone: 0.25,
            darkZone: 0.50,
            lightColor: { r: 248, g: 250, b: 242 },
            darkColor: { r: 185, g: 193, b: 205 },
            verticalDarken: 0.1
        };

        this.gradientImage = null; // тут зберігатимемо готовий ImageData

        this.init();
    }

    init() {
        this.canvas.width = window.innerWidth || 800;
        this.canvas.height = window.innerHeight || 600;
        this.createGradient();  // один раз створюємо градієнт
        this.draw();            // малюємо його на канвасі
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.createGradient();  // пересоздаємо лише при зміні розміру
        this.draw();
    }

    interpolateColor(color1, color2, t) {
        return {
            r: Math.round(color1.r + (color2.r - color1.r) * t),
            g: Math.round(color1.g + (color2.g - color1.g) * t),
            b: Math.round(color1.b + (color2.b - color1.b) * t)
        };
    }

    createGradient() {
        this.ctx.fillStyle = `rgb(${this.config.darkColor.r}, ${this.config.darkColor.g}, ${this.config.darkColor.b})`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        const width = this.canvas.width;
        const height = this.canvas.height;

        const imageData = this.ctx.createImageData(width, height);
        const data = imageData.data;

        const { waveAmplitude, waveFrequency, leftZone, darkZone,
                lightColor, darkColor, verticalDarken } = this.config;

        const leftZoneEnd = leftZone;
        const darkZoneEnd = leftZone + darkZone;
        const waveAmp = width * waveAmplitude;

        for (let y = 0; y < height; y++) {
            const angle = (y / height) * waveFrequency * Math.PI * 2;
            const waveOffset = Math.sin(angle) * waveAmp;

            for (let x = 0; x < width; x++) {
                const adjustedPos = x + waveOffset;
                let gradientPos = adjustedPos / width;
                gradientPos = Math.max(0, Math.min(1, gradientPos));

                let color;

                if (gradientPos < leftZoneEnd) {
                    const t = gradientPos / leftZoneEnd;
                    color = this.interpolateColor(lightColor, darkColor, t);
                } else if (gradientPos < darkZoneEnd) {
                    color = { ...darkColor };
                } else {
                    const t = (gradientPos - darkZoneEnd) / (1 - darkZoneEnd);
                    color = this.interpolateColor(darkColor, lightColor, t);
                }

                const verticalFactor = 1 - (y / height) * verticalDarken;
                color.r = Math.round(color.r * verticalFactor);
                color.g = Math.round(color.g * verticalFactor);
                color.b = Math.round(color.b * verticalFactor);

                const index = (y * width + x) * 4;
                data[index] = color.r;
                data[index + 1] = color.g;
                data[index + 2] = color.b;
                data[index + 3] = 255;
            }
        }

        this.gradientImage = imageData; // зберігаємо готове зображення
    }

    draw() {
    if (this.gradientImage) {
        this.ctx.putImageData(this.gradientImage, 0, 0);
        // плавно показати канвас
        this.canvas.style.opacity = 1;
    }
}
}

// Ініціалізація градієнта
document.addEventListener('DOMContentLoaded', function() {
    new WaveGradient('gradient-canvas');
});
