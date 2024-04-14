import java.sql.*;
import java.util.HashSet;
import java.util.Map;
import java.util.HashMap;
import java.util.Collections;

public class NearestNeighbor 
{
	static double jaccard(HashSet<String> s1, HashSet<String> s2) {
		int total_size = s1.size() + s2.size();
		int i_size = 0;
		for(String s: s1) {
			if (s2.contains(s))
				i_size++;
		}
		return ((double) i_size)/(total_size - i_size);
	}
	public static void executeNearestNeighbor() {
		/************* 
		 * Add your code to add a new column to the users table (set to null by default), calculate the nearest neighbor for each node (within first 5000), and write it back into the database for those users..
		 ************/
		Connection connection = null;
		try {
			connection = DriverManager.getConnection("jdbc:postgresql://localhost:5432/stackexchange","root", "root");
		} catch (SQLException e) {
			System.out.println("Connection Failed! Check output console");
			e.printStackTrace();
			return;
		}

		if (connection != null) {
			System.out.println("You made it, take control your database now!");
		} else {
			System.out.println("Failed to make connection!");
			return;
		}

		Map<Integer, HashSet<String>> userTags = new HashMap<>();

		try (Statement stmt = connection.createStatement()) {
			String addNearestNeighbour = "ALTER TABLE users ADD COLUMN nearest_neighbor integer default null;";
			stmt.execute(addNearestNeighbour);
			String fetchData = "select users.id, array_remove(array_agg(posts.tags), null) as arr " +
								"from users, posts " +
								"where users.id = posts.OwnerUserId and users.id < 5000 " +
								"group by users.id " +
								"having count(posts.tags) > 0;";
			ResultSet rs = stmt.executeQuery(fetchData);
			while (rs.next()) {
				int id = rs.getInt("id");
				Array arr = rs.getArray("arr");
				String[] tags = (String[]) arr.getArray();
				HashSet<String> tagSet = new HashSet<>();
				for (String tag: tags) {
					Collections.addAll(tagSet, tag.replaceAll("<", "").replaceAll(">", " ").trim().split("\\s+"));
				}
				userTags.put(id, tagSet);
			}

			for (Map.Entry<Integer, HashSet<String>> entry : userTags.entrySet()) {
				int userId = entry.getKey();
				HashSet<String> userSet = entry.getValue();
				int nearestNeighborId = -1;
				double maxSimilarity = 0;
	
				for (Map.Entry<Integer, HashSet<String>> compareEntry : userTags.entrySet()) {
					int compareUserId = compareEntry.getKey();
					if (userId == compareUserId) continue; // Skip self comparison
	
					double similarity = jaccard(userSet, compareEntry.getValue());
					if (similarity > maxSimilarity || (similarity == maxSimilarity && compareUserId < nearestNeighborId)) {
						maxSimilarity = similarity;
						nearestNeighborId = compareUserId;
					}
				}

				if (nearestNeighborId != -1) {
                    String updateSQL = "UPDATE users SET nearest_neighbor = ? WHERE id = ?";
                    try (PreparedStatement updateStmt = connection.prepareStatement(updateSQL)) {
                        updateStmt.setInt(1, nearestNeighborId);
                        updateStmt.setInt(2, userId);
                        updateStmt.executeUpdate();
                    }
                }
			}

			connection.commit();
			
		} catch (SQLException e ) {
			System.out.println(e);
		}
	}

	public static void main(String[] argv) {
		executeNearestNeighbor();
	}
}
