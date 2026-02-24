import javax.swing.*;
import java.awt.*;

public class Main {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame();
            frame.setUndecorated(true);
            frame.setExtendedState(JFrame.MAXIMIZED_BOTH);
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

            Color[] colors = {
                Color.RED,
                Color.ORANGE,
                Color.YELLOW,
                Color.GREEN,
                Color.CYAN,
                Color.BLUE,
                new Color(128, 0, 128) // 紫色
            };

            ColorPanel panel = new ColorPanel(colors);

            frame.add(panel);
            frame.setVisible(true);

            new Thread(() -> {
                while (true) {
                    try {
                        Thread.sleep(10); // 50 ms - smaller is faster
                    } catch (InterruptedException e) {
                        break;
                    }
                    SwingUtilities.invokeLater(panel::nextColor);
                }
            }).start();
        });
    }

    static class ColorPanel extends JPanel {
        private final Color[] colors;
        private int idx = 0;

        ColorPanel(Color[] colors) {
            this.colors = colors;
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            g.setColor(colors[idx]);
            g.fillRect(0, 0, getWidth(), getHeight());
        }

        public void nextColor() {
            idx = (idx + 1) % colors.length;
            repaint();
        }
    }
}